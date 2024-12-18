"""Tests for the SonnenBatterie config flow.
    Using emulated sonnenbatterie driver package: sonnenbatterie_api_v2
    which uses API token via sonnen_api_v2 package. No support for user/pwassword authentication.
"""


from unittest.mock import patch

from sonnen_api_v2 import Batterie, BatterieError
#from sonnen.inverters import X1MiniV34
import sonnenbatterie
from . mock_sonnenbatterie_v2_charging import __mock_configurations #, __mock_status_charging, __mock_latest_charging, __mock_battery, __mock_powermeter, __mock_inverter
from homeassistant import config_entries

from custom_components.sonnenbatterie.const import DOMAIN
from homeassistant.const import CONF_IP_ADDRESS, CONF_PORT, CONF_USERNAME, CONF_API_TOKEN, CONF_MODEL, CONF_DEVICE_ID
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.config_entries import ConfigEntry


def __mock_async_step_token_success():
    return ConfigEntry(
        title='192.168.100.200  (api token)',
        data={
            CONF_USERNAME: '#api_token',
            CONF_MODEL: 'Power unit Evo IP56',
            CONF_DEVICE_ID: '321123',
            CONF_API_TOKEN: 'token',
            CONF_IP_ADDRESS: '192.168.100.200',
            CONF_PORT: '80',
        },
    )

def __mock_get_token_data():
#type SonnenConfigEntry = ConfigEntry[SonnenData]
    return ConfigEntry(
        title='192.168.100.200  (api token)',
        data={
            CONF_USERNAME: '#api_token',
            CONF_MODEL: 'Power unit Evo IP56',
            CONF_DEVICE_ID: '321123',
            CONF_API_TOKEN: 'token',
            CONF_IP_ADDRESS: '192.168.100.200',
            CONF_PORT: '80',
        },
    )

async def test_form_success(hass: HomeAssistant) -> None:
    """Test successful form."""
    flow = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert flow["type"] is FlowResultType.FORM
    assert flow["errors"] == {}

    with (
        patch(
            "homeassistant.custom_components.sonnenbatterie.config_flow.async_step_token",
            return_value=__mock_async_step_token_success(),
        ),
        # patch("Batterie.fetch_status", return_value=__mock_status_charging()),
        # patch("Batterie.fetch_latest_details", return_value=__mock_latest_charging()),
        patch("Batterie.fetch_configurations", return_value=__mock_configurations()),
        # patch("Batterie.fetch_battery_status", return_value=__mock_battery()),
        # patch("Batterie.fetch_powermeter", return_value=__mock_powermeter()),
        # patch("Batterie.fetch_inverter", return_value=__mock_inverter()),
        patch(
            "homeassistant.custom_components.sonnenbatterie.async_setup_entry",
            return_value=True,
        ) as mock_setup_entry,
    ):
        entry_result = await hass.config_entries.flow.async_configure(
            flow["flow_id"],
            {
            CONF_USERNAME: '#api_token',
            CONF_MODEL: 'Power unit Evo IP56',
            CONF_DEVICE_ID: '321123',
            CONF_API_TOKEN: 'token',
            CONF_IP_ADDRESS: '192.168.100.200',
            CONF_PORT: '80',
            },
        )
        await hass.async_block_till_done()

    assert entry_result["type"] is FlowResultType.CREATE_ENTRY
    assert entry_result["title"] == '192.168.100.200  (api token)'
    assert entry_result["data"] == {
            CONF_USERNAME: '#api_token',
            CONF_MODEL: 'Power unit Evo IP56',
            CONF_DEVICE_ID: '321123',
            CONF_API_TOKEN: 'token',
            CONF_IP_ADDRESS: '192.168.100.200',
            CONF_PORT: '80',
    }
    assert len(mock_setup_entry.mock_calls) == 1


async def test_form_connect_error(hass: HomeAssistant) -> None:
    """Test cannot connect form."""
    flow = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert flow["type"] is FlowResultType.FORM
    assert flow["errors"] == {}

    with patch(
        "homeassistant.custom_components.sonnenbatterie.config_flow.async_step_token",
        side_effect=BatterieError,
    ):
        entry_result = await hass.config_entries.flow.async_configure(
            flow["flow_id"],
            {
            CONF_USERNAME: '#api_token',
            CONF_MODEL: 'Power unit Evo IP56',
            CONF_DEVICE_ID: '321123',
            CONF_API_TOKEN: 'token',
            CONF_IP_ADDRESS: '192.168.100.200',
            CONF_PORT: '80',
            },
        )

    assert entry_result["type"] is FlowResultType.FORM
    assert entry_result["errors"] == {"base": "cannot_connect"}


async def test_form_unknown_error(hass: HomeAssistant) -> None:
    """Test unknown error form."""
    flow = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert flow["type"] is FlowResultType.FORM
    assert flow["errors"] == {}

    with patch(
        "homeassistant.custom_components.sonnenbatterie.config_flow.async_step_token",
        side_effect=Exception,
    ):
        entry_result = await hass.config_entries.flow.async_configure(
            flow["flow_id"],
            {
            CONF_USERNAME: '#api_token',
            CONF_MODEL: 'Power unit Evo IP56',
            CONF_DEVICE_ID: '321123',
            CONF_API_TOKEN: 'token',
            CONF_IP_ADDRESS: '192.168.100.200',
            CONF_PORT: '80',
            },
        )

    assert entry_result["type"] is FlowResultType.FORM
    assert entry_result["errors"] == {"base": "unknown"}
