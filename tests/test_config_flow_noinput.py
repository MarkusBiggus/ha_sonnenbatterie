from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.sonnenbatterie import async_setup_entry

from custom_components.sonnenbatterie.const import DOMAIN

from homeassistant.config_entries import SOURCE_USER
from homeassistant.const import (
    CONF_PASSWORD,
    CONF_USERNAME,
    CONF_IP_ADDRESS,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    CONF_API_TOKEN,
    CONF_DEVICE_ID,
    CONF_MODEL
)
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from tests.common import MockConfigEntry

@pytest.mark.usefixtures("mock_default_requests")
async def test_flow_works(hass: HomeAssistant, mock_discovery) -> None:
    """Test config flow."""
    mock_discovery.return_value = "1"
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "token"
    # assert result["data_schema"]({CONF_USERNAME: "", CONF_PASSWORD: ""}) == {
    #         CONF_USERNAME: '#api_token',
    #         CONF_MODEL: 'Power unit Evo IP56',
    #         CONF_DEVICE_ID: '321123',
    #         CONF_API_TOKEN: 'token',
    #         CONF_IP_ADDRESS: '192.168.100.200',
    #         CONF_PORT: '80',
    # }

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={
            CONF_USERNAME: '#api_token',
            CONF_MODEL: 'Power unit Evo IP56',
            CONF_DEVICE_ID: '321123',
            CONF_API_TOKEN: 'token',
            CONF_IP_ADDRESS: '192.168.100.200',
            CONF_PORT: '80',
        },
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "192.168.100.200  (api token)"
    assert result["data"] == {
            CONF_USERNAME: '#api_token',
            CONF_MODEL: 'Power unit Evo IP56',
            CONF_DEVICE_ID: '321123',
            CONF_API_TOKEN: 'token',
            CONF_IP_ADDRESS: '192.168.100.200',
            CONF_PORT: '80',
    }


@pytest.mark.usefixtures("mock_setup_entry", "mock_sonnenbatterie")
async def test_flow_user_step_no_input(hass: HomeAssistant):
    """Test appropriate error when no input is provided."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )

    assert {"base": "missing"} == result["errors"]
    assert result.get("step_id") == "user"
    assert result.get("type") is FlowResultType.FORM

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={}
    )
    assert result.get("title") == "192.168.100.200  (api token)"
    assert result.get("type") is FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_IP_ADDRESS] == "192.168.1.123"
    assert result["result"].unique_id == "321123"

@pytest.mark.usefixtures("mock_setup_entry", "mock_sonnenbatterie")
async def test_flow_token_step_no_input(hass: HomeAssistant):
    """Test appropriate error when no input is provided."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert {"base": "missing"} == result["errors"]
    assert result.get("step_id") == "user"
    assert result.get("type") is FlowResultType.FORM

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={}
    )
    assert {"base": "missing"} == result["errors"]
    assert result.get("title") == "192.168.100.200  (api token)"
    assert result.get("type") is FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_IP_ADDRESS] == "192.168.1.123"
    assert result["result"].unique_id == "321123"

async def test_options_flow(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry
) -> None:
    """Test options config flow."""
    mock_config_entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(mock_config_entry.entry_id)

    assert result.get("type") is FlowResultType.FORM
    assert result.get("step_id") == "init"

    result2 = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={CONF_IP_ADDRESS: '192.168.100.200'},
    )

    assert result2.get("type") is FlowResultType.CREATE_ENTRY
    assert result2.get("data") == {
            CONF_USERNAME: '#api_token',
            CONF_MODEL: 'Power unit Evo IP56',
            CONF_DEVICE_ID: '321123',
            CONF_API_TOKEN: 'token',
            CONF_IP_ADDRESS: '192.168.100.200',
            CONF_PORT: '80',
    }