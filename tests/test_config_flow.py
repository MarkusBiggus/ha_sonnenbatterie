"""Tests for the SonnenBatterie config flow."""

from unittest.mock import patch

# from sonnen_api_v2 import RealTimeAPI
from sonnen_api_v2 import BatterieError
#from sonnen.inverters import X1MiniV34
import sonnenbatterie
from mock_sonnenbatterie import __mock_status_charging, __mock_configurations, __mock_battery, __mock_powermeter, __mock_inverter
from homeassistant import config_entries
from custom_components.sonnenbatterie.const import DOMAIN
from homeassistant.const import CONF_IP_ADDRESS, CONF_PASSWORD, CONF_PORT, CONF_USERNAME, CONF_API_TOKEN
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.config_entries import ConfigEntry


def __mock_async_step_user_success():
    return ConfigEntry(
        title='192.168.100.200 (usr/pwd)',
        data={
            CONF_USERNAME: 'username',
            CONF_PASSWORD: 'password',
            CONF_IP_ADDRESS: '192.168.100.200',
        },
    )


def __mock_get_user_data():
#type SonnenConfigEntry = ConfigEntry[SonnenData]
    return ConfigEntry(
        title='192.168.100.200 (usr/pwd)',
        data={
            CONF_USERNAME: 'username',
            CONF_PASSWORD: 'password',
            CONF_IP_ADDRESS: '192.168.100.200',
        },
    )

def __mock_get_token_data():
#type SonnenConfigEntry = ConfigEntry[SonnenData]
    return ConfigEntry(
        title='192.168.100.200  (api token)',
        data={
            CONF_USERNAME: '#api_token',
            CONF_API_TOKEN: 'token',
            CONF_IP_ADDRESS: '192.168.100.200',
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
            "homeassistant.custom_components.sonnenbatterie.config_flow.async_step_user",
            return_value=__mock_async_step_user_success(),
        ),
        patch("sonnen_api_v2.get_status", return_value=__mock_status_charging()),
        patch("sonnen_api_v2.get_battery", return_value=__mock_battery()),
        patch("sonnen_api_v2.get_inverter", return_value=__mock_inverter()),
        patch("sonnen_api_v2.get_powermeter", return_value=__mock_powermeter()),
        patch("sonnen_api_v2.get_systemdata", return_value=__mock_status_charging()),
        patch("sonnen_api_v2.get_configurations", return_value=__mock_configurations()),
        # patch("sonnenbatterie.get_status", return_value=__mock_status_charging()),
        # patch("sonnenbatterie.get_battery", return_value=__mock_battery()),
        # patch("sonnenbatterie.get_inverter", return_value=__mock_inverter()),
        # patch("sonnenbatterie.get_powermeter", return_value=__mock_powermeter()),
        patch(
            "homeassistant.custom_components.sonnenbatterie.async_setup_entry",
            return_value=True,
        ) as mock_setup_entry,
    ):
        entry_result = await hass.config_entries.flow.async_configure(
            flow["flow_id"],
            {CONF_IP_ADDRESS: "192.168.100.200", CONF_USERNAME: 'username', CONF_PASSWORD: "password"},
        )
        await hass.async_block_till_done()

    assert entry_result["type"] is FlowResultType.CREATE_ENTRY
    assert entry_result["title"] == '192.168.100.200 (usr/pwd)'
    assert entry_result["data"] == {
        CONF_IP_ADDRESS: "192.168.100.200",
        CONF_USERNAME: 'username',
        CONF_PASSWORD: "password",
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
        "homeassistant.custom_components.sonnenbatterie.config_flow.async_step_user",
        side_effect=BatterieError,
    ):
        entry_result = await hass.config_entries.flow.async_configure(
            flow["flow_id"],
            {CONF_IP_ADDRESS: "192.168.100.200", CONF_USERNAME: 'username', CONF_PASSWORD: "password"},
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
        "homeassistant.custom_components.sonnenbatterie.config_flow.async_step_user",
        side_effect=Exception,
    ):
        entry_result = await hass.config_entries.flow.async_configure(
            flow["flow_id"],
            {CONF_IP_ADDRESS: "192.168.100.200", CONF_USERNAME: 'username', CONF_PASSWORD: "password"},
        )

    assert entry_result["type"] is FlowResultType.FORM
    assert entry_result["errors"] == {"base": "unknown"}
