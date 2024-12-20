# pylint: disable=no-name-in-module
from sonnenbatterie import sonnenbatterie

# pylint: enable=no-name-in-module
import traceback

# import logging
import voluptuous as vol
from homeassistant import config_entries, core
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv

from .const import (
    DOMAIN,
    LOGGER,
    CONFIG_SCHEMA_BASE,
    CONFIG_SCHEMA_PASSWORD,
    CONFIG_SCHEMA_TOKEN,
    DEFAULT_SCAN_INTERVAL,
    ATTR_SONNEN_DEBUG,
    DEFAULT_SONNEN_DEBUG
)

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

class SonnenbatterieFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    # The schema version of the entries that it creates
    VERSION = 1

    def __init__(self):
        """Initialize."""
        self.user_info = {}

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        self.data_schema = CONFIG_SCHEMA_BASE
        LOGGER.info("async_step_user.")

        if not user_input:
            LOGGER.info("async_step_user: _show_form")
            return self._show_form()

        use_token = user_input['use_token']
        self.user_info = user_input
        # Return the form of the next step
        if use_token:
        #    token_input = user_input if CONF_API_TOKEN in user_input else None
            return await self.async_step_token(user_input)
        else:
        #    password_input = user_input if CONF_PASSWORD in user_input else None
            return await self.async_step_password(user_input)

        # self.user_info = user_input
        # return await self.async_step_progress()

    @callback
    def _show_form(self, errors=None):
        """Show base form to the user."""
        return self.async_show_form(
            step_id="user",
            data_schema=self.data_schema,
            errors=errors if errors else {},
        )

    async def async_step_password(self, user_input=None):
        """Handle a flow initialized by the user."""
        self.data_schema = CONFIG_SCHEMA_PASSWORD
        LOGGER.info("async_step_password.")
        if CONF_PASSWORD not in user_input:
            LOGGER.info("async_step_password: _show_form")
            return self._show_form()
            return self._show_form_A()

        ip_address = self.user_info[CONF_IP_ADDRESS]
        ip_port = self.user_info[CONF_PORT]
        username = user_input[CONF_USERNAME]
        password = user_input[CONF_PASSWORD]

        def _internal_setup(_username, _password, _ipaddress):
            return sonnenbatterie(_username, _password, _ipaddress)

        try:
            sonnenInst = await self.hass.async_add_executor_job(
                _internal_setup, username, password, ip_address
            )
        except Exception:
            e = traceback.format_exc()
            LOGGER.error("Unable to connect to sonnenbatterie: %s", e)
            # if ex.errcode == 400:
            #    return self._show_form({"base": "invalid_credentials"})
            return self._show_form_A(errors={"base": "connection_error"})

        self.title = user_input[CONF_IP_ADDRESS] + ' (usr/pwd)'
        self.user_info.update(user_input)
        # return self.async_show_progress(
        #     step_id="progress",
        #     progress_action="Password",
        # )
        return self.async_create_entry(
            title=self.title,
            data={
                CONF_IP_ADDRESS: ip_address,
                CONF_PORT: ip_port,
                'use_token': False,
                CONF_USERNAME: username,
                CONF_PASSWORD: password,
            },
        )

    @callback
    def _show_form_A(self, errors=None):
        """Show the password form to the user."""
        LOGGER.info("Show password form to the user.")
        return self.async_show_form(
            step_id="password",
            data_schema=self.data_schema,
            errors=errors if errors else {},
        )

    async def async_step_token(self, user_input=None):
#    ) -> config_entries.ConfigFlowResult:
        """Handle a flow initialized by the user."""
        self.data_schema = CONFIG_SCHEMA_TOKEN
        LOGGER.info("async_step_token.")

        if CONF_API_TOKEN not in user_input:
            LOGGER.info("async_step_token: _show_form_B")
            return self._show_form_B()
#            print(f'form_B: {user_input}')

        username = '#api_token'
        ip_address = self.user_info[CONF_IP_ADDRESS]
        ip_port = self.user_info[CONF_PORT]
        api_token = user_input[CONF_API_TOKEN]
        model_id = user_input[CONF_MODEL]
        device_id = user_input[CONF_DEVICE_ID]

        def _internal_setup(_username, _apitoken, _ipaddress, _ipport):
            return sonnenbatterie(_username, _apitoken, _ipaddress, _ipport) #API V2

        try:
            sonnenInst = await self.hass.async_add_executor_job(
            _internal_setup, username, api_token, ip_address, ip_port
            )

        except Exception:
            e = traceback.format_exc()
        #    LOGGER.error("Unable to connect to sonnenbatterie: %s", e)
            LOGGER.error(f'Unable to connect to sonnenbatterie: {e}')
            # if ex.errcode == 400:
            #    return self._show_form({"base": "invalid_credentials"})
            return self._show_form_B(errors={"base": "connection_error"})

        self.title = user_input[CONF_IP_ADDRESS] + ' (api token)'
        self.user_info.update(user_input)
        # return self.async_show_progress(
        #     progress_action="Token.",
        #     progress_task="self.async_step_token"
        # )
        return self.async_create_entry(
            title=self.title,
            data={
                CONF_IP_ADDRESS: ip_address,
                CONF_PORT: ip_port,
                'use_token': True,
                CONF_USERNAME: username,
                CONF_API_TOKEN: api_token,
                CONF_MODEL: model_id,
                CONF_DEVICE_ID: device_id,
            },
        )

    @callback
    def _show_form_B(self, errors=None):
        """Show token form to the user."""
        LOGGER.info("Show token form to the user.")
        return self.async_show_form(
            step_id="token",
            data_schema=self.data_schema,
            errors=errors if errors else {},
        )

    # async def async_step_progress(
    #     self, user_input: str | None = None
    # ) -> config_entries.ConfigFlowResult:
    #     """Displaying progress for two tasks"""
    #     LOGGER.info("async_step_progress")
    #     # if not self.task_one or not self.task_two:
    #     #     if not self.task_one:
    #     #         task = asyncio.sleep(10)
    #     #         LOGGER.info("scheduling task1")
    #     #         self.task_one = self.hass.async_create_task(self._async_do_task(task))
    #     #         progress_action = "task_one"
    #     #     else:
    #     #         task = asyncio.sleep(10)
    #     #         LOGGER.info("scheduling task2")
    #     #         self.task_two = self.hass.async_create_task(self._async_do_task(task))
    #     #         progress_action = "task_two"
    #     #     LOGGER.info("showing_progress: %s", progress_action)
    #     #     return self.async_show_progress(
    #     #         step_id="progress",
    #     #         progress_action=progress_action,

    #     #     )
    #     # if CONF_API_TOKEN in self.user_info or CONF_PASSWORD in self.user_info:
    #     #     LOGGER.info("async_step_progress - all tasks done")
    #     #     return self.async_show_progress_done(next_step_id="finish")

    #     user_input = self.user_info
    #     self.title = user_input[CONF_IP_ADDRESS] + ' (api token)'
    #     # Return the form of the next step
    #     if user_input['use_token']:
    #         token_input = user_input if CONF_API_TOKEN in user_input else None
    #         next_input = await self.async_step_token(token_input)
    #     else:
    #         password_input = user_input if CONF_PASSWORD in user_input else None
    #         await self.async_step_password(password_input)

    #     LOGGER.info("async_step_progress - all tasks done")
    #     return self.async_show_progress_done(next_step_id="finish")

    # async def _async_do_task(self, task):
    #     LOGGER.info("task pre")
    #     await task  # A task that take some time to complete.
    #     LOGGER.info("task done")
    #     # Ensure we go back to the flow
    #     self.hass.async_create_task(
    #         self.hass.config_entries.flow.async_configure(flow_id=self.flow_id)
    #     )

    # async def async_step_finish(
    #     self, user_input: str | None = None
    # ) -> config_entries.ConfigFlowResult:
    #     LOGGER.info("async_step_finish")
    #     return self.async_create_entry(
    #         title=self.title,
    #         data=self.user_info,
    #     )

    # async def async_step_import(self, import_config):
    #     """Import a config entry from configuration.yaml."""
    # #????    return await self.async_step_user(import_config)
    #     return await self.async_step_token(import_config)

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

        OPTIONS_SCHEMA = vol.Schema(
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
        )

        if self.options[CONF_USERNAME] == '#api_token':
            data_schema = self.add_suggested_values_to_schema(
                OPTIONS_SCHEMA, OPTIONS_SCHEMA
            )
        else:
            data_schema = OPTIONS_SCHEMA


        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
        )

    async def _update_options(self):
        """Update config entry options."""
        return self.async_create_entry(title="", data=self.options)
