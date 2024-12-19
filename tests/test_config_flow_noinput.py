""" pytest tests/test_config_flow_noinput.py -s -c
"""
from unittest.mock import AsyncMock, MagicMock

import pytest

#from custom_components.sonnenbatterie import async_setup_entry

from custom_components.sonnenbatterie.const import DOMAIN, CONFIG_SCHEMA_TOKEN

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

from  tests.battery_charging_coroutine import fixture_battery_charging

#from tests.common import MockConfigEntry

pytestmark = pytest.mark.usefixtures("mock_setup_entry", "mock_unload_entry")#, "battery_charging")

#@pytest.mark.asyncio
#@pytest.mark.usefixtures("battery_charging")
async def test_show_form(hass: HomeAssistant) -> None:
    """Test that the form is served with no input."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER} # flow init step is always the source name
    )
#    print(f'result: {result}')
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"


@pytest.mark.parametrize("ip_address", ["192.168.100.200"]) #, "192.168.88.11"])
@pytest.mark.usefixtures("battery_charging")
async def test_token_create_entry(hass: HomeAssistant, ip_address: str) -> None:
    """Test that the token step works.
        fetch_configuration coroutine must be mocked so sonnenbatterie instantiation works
        to verify IP & auth details are correct.
    """
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_USER},
        data={
            CONF_IP_ADDRESS: ip_address, # '192.168.100.200',
            CONF_PORT: '80',
            'use_token': 'True',
            CONF_USERNAME: '#api_token',
            CONF_API_TOKEN: 'token',
            CONF_MODEL: 'Power unit Evo IP56',
            CONF_DEVICE_ID: '321123',
            },
    )
    print(f'result: {result}')
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == (f'{ip_address}  (api token)')
    assert result["data"][CONF_IP_ADDRESS] == ip_address # '192.168.100.200'
    assert result["data"][CONF_MODEL] == 'Power unit Evo IP56'
    assert result["data"][CONF_USERNAME] == '#api_token'

# async def test_device_exists_abort(
#     hass: HomeAssistant,
#     mock_config_entry: MockConfigEntry,
# ) -> None:
#     """Test we abort config flow if Sonnen Batterie already configured."""

#     result = await hass.config_entries.flow.async_init(
#         DOMAIN, context={"source": SOURCE_USER}, data=CONFIG_SCHEMA_B
#     )

#     assert result["type"] is FlowResultType.ABORT
#     assert result["reason"] == "already_configured"


@pytest.mark.usefixtures("mock_default_requests")
async def test_token_flow_works(hass: HomeAssistant, mock_discovery) -> None:
    """Test config flow."""
    mock_discovery.return_value = "1"
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "init"
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
            CONF_IP_ADDRESS: '192.168.100.200',
            CONF_PORT: '80',
            'use_token': 'True',
            CONF_API_TOKEN: 'token',
            CONF_MODEL: 'Power unit Evo IP56',
            CONF_DEVICE_ID: '321123',
        },
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "192.168.100.200  (api token)"
    assert result["data"] == {
            CONF_IP_ADDRESS: '192.168.100.200',
            CONF_PORT: '80',
            'use_token': 'True',
            CONF_USERNAME: '#api_token',
            CONF_API_TOKEN: 'token',
            CONF_MODEL: 'Power unit Evo IP56',
            CONF_DEVICE_ID: '321123',
    }


@pytest.mark.usefixtures("mock_setup_entry", "mock_sonnenbatterie")
async def test_flow_user_step_no_input(hass: HomeAssistant):
    """Test appropriate error when no input is provided."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert {"base": "missing"} == result["errors"]
    assert result.get("step_id") == "init"
    assert result.get("type") is FlowResultType.FORM

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={}
    )
    assert result.get("title") == "192.168.100.200  (api token)"
    assert result.get("type") is FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_IP_ADDRESS] == "192.168.100.200"
    assert result["result"].unique_id == "321123"

# @pytest.mark.usefixtures("mock_setup_entry", "mock_sonnenbatterie")
# async def test_flow_token_step_no_input(hass: HomeAssistant):
#     """Test appropriate error when no input is provided."""
#     result = await hass.config_entries.flow.async_init(
#         DOMAIN, context={"source": SOURCE_USER}
#     )
#     assert {"base": "missing"} == result["errors"]
#     assert result.get("step_id") == "token"
#     assert result.get("type") is FlowResultType.FORM

#     result = await hass.config_entries.flow.async_configure(
#         result["flow_id"], user_input={}
#     )
#     assert {"base": "missing"} == result["errors"]
#     assert result.get("title") == "192.168.100.200  (api token)"
#     assert result.get("type") is FlowResultType.CREATE_ENTRY
#     assert result["data"][CONF_IP_ADDRESS] == "192.168.1.123"
#     assert result["result"].unique_id == "321123"

# async def test_options_flow(
#     hass: HomeAssistant, mock_config_entry #: MockConfigEntry
# ) -> None:
#     """Test options config flow."""
#     mock_config_entry.add_to_hass(hass)

#     result = await hass.config_entries.options.async_init(mock_config_entry.entry_id)

#     assert result.get("type") is FlowResultType.FORM
#     assert result.get("step_id") == "init"

#     result2 = await hass.config_entries.options.async_configure(
#         result["flow_id"],
#         user_input={CONF_IP_ADDRESS: '192.168.100.200'},
#     )

#     assert result2.get("type") is FlowResultType.CREATE_ENTRY
#     assert result2.get("data") == {
#             CONF_USERNAME: '#api_token',
#             CONF_MODEL: 'Power unit Evo IP56',
#             CONF_DEVICE_ID: '321123',
#             CONF_API_TOKEN: 'token',
#             CONF_IP_ADDRESS: '192.168.100.200',
#             CONF_PORT: '80',
#     }