# pylint: disable=no-name-in-module
from sonnenbatterie import sonnenbatterie

# pylint: enable=no-name-in-module
import traceback

# import logging
# import voluptuous as vol
from homeassistant import config_entries, core
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv

# pylint: disable=unused-wildcard-import
from .const import *  #

# pylint: enable=unused-wildcard-import
import voluptuous as vol
from homeassistant.const import (
    CONF_PASSWORD,
    CONF_USERNAME,
    CONF_IP_ADDRESS,
    CONF_SCAN_INTERVAL,
    CONF_API_TOKEN,
)

import os
from dotenv import load_dotenv
load_dotenv()

BATTERIE_HOST = os.getenv("BATTERIE_HOST", "X")
API_READ_TOKEN = os.getenv("API_READ_TOKEN", "X")
API_WRITE_TOKEN = os.getenv("API_WRITE_TOKEN", "X")


class SonnenbatterieFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    def __init__(self):
        """Initialize."""
        self.data_schema = CONFIG_SCHEMA_A

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        # if self._async_current_entries():
        #    return self.async_abort(reason="single_instance_allowed")

#        return self._show_form()

        username = user_input[CONF_USERNAME]
        password = user_input[CONF_PASSWORD]
        ipaddress = user_input[CONF_IP_ADDRESS]

        try:

            def _internal_setup(_username, _password, _ipaddress):
                return sonnenbatterie(_username, _password, _ipaddress)

            sonnen_inst = await self.hass.async_add_executor_job(
                _internal_setup, username, password, ipaddress
            )
            # sonnenbatterie(username,password,ipaddress)
            # await self.hass.async_add_executor_job(
            #    Abode, username, password, True, True, True, cache
            # )

        except Exception:
            e = traceback.format_exc()
        #    LOGGER.error("Unable to connect to sonnenbatterie: %s", e)
            LOGGER.error(f'Unable to connect to sonnenbatterie: {e}')
            # if ex.errcode == 400:
            #    return self._show_form({"base": "invalid_credentials"})
            return self._show_form({"base": "connection_error"})

        return self.async_create_entry(
            title=user_input[CONF_IP_ADDRESS],
            data={
                CONF_USERNAME: username,
                CONF_PASSWORD: password,
                CONF_IP_ADDRESS: ipaddress,
            },
        )

    @callback
    def _show_form(self, errors=None):
        """Show the form to the user."""
        return self.async_show_form(
            step_id="user",
            data_schema=self.data_schema,
            errors=errors if errors else {},
        )

    async def async_step_token(self, user_input=None):
        """Handle a flow initialized by the user."""
        # if self._async_current_entries():
        #    return self.async_abort(reason="single_instance_allowed")

        if not user_input:
            API_TOKEN = API_WRITE_TOKEN if API_WRITE_TOKEN != "X" else API_READ_TOKEN
            if BATTERIE_HOST == "X" or API_TOKEN == "X":
                print(f"host: {BATTERIE_HOST} WRITE: {API_WRITE_TOKEN} READ: {API_READ_TOKEN}")
                raise ValueError(
                    "Set BATTERIE_HOST & API_READ_TOKEN or API_WRITE_TOKEN in .env See sonnenbatterie package env.example"
                )
            user_input = {CONF_API_TOKEN:API_TOKEN, CONF_IP_ADDRESS:BATTERIE_HOST}

#            return self._show_form_B()

        apitoken = user_input[CONF_API_TOKEN]
        ipaddress = user_input[CONF_IP_ADDRESS]

        try:

            def _internal_setup(_apitoken, _ipaddress):
                return sonnenbatterie(_apitoken, _ipaddress) #API V2

            sonnen_inst = await self.hass.async_add_executor_job(
                _internal_setup, apitoken, ipaddress
            )

        except Exception:
            e = traceback.format_exc()
        #    LOGGER.error("Unable to connect to sonnenbatterie: %s", e)
            LOGGER.error(f'Unable to connect to sonnenbatterie: {e}')
            # if ex.errcode == 400:
            #    return self._show_form({"base": "invalid_credentials"})
            return self._show_form_B({"base": "connection_error"})

        return self.async_create_entry(
            title=user_input[CONF_IP_ADDRESS],
            data={
                CONF_API_TOKEN: apitoken,
                CONF_IP_ADDRESS: ipaddress,
            },
        )

    @callback
    def _show_form_B(self, errors=None):
        """Show token form to the user."""
        return self.async_show_form(
            step_id="token",
            data_schema=self.data_schema,
            errors=errors if errors else {},
        )

    async def async_step_import(self, import_config):
        """Import a config entry from configuration.yaml."""
        # if self._async_current_entries():
        #    LOGGER.warning("Only one configuration of abode is allowed.")
        #    return self.async_abort(reason="single_instance_allowed")

    #????    return await self.async_step_user(import_config)
        return await self.async_step_token(import_config)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry
        self.options = dict(config_entry.options)

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=self.config_entry.options.get(
                            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                        ),
                    ): cv.positive_int,
                    vol.Optional(
                        ATTR_SONNEN_DEBUG,
                        default=self.config_entry.options.get(
                            ATTR_SONNEN_DEBUG, DEFAULT_SONNEN_DEBUG
                        ),
                    ): bool,
                }
            ),
        )

    async def _update_options(self):
        """Update config entry options."""
        return self.async_create_entry(title="", data=self.options)
