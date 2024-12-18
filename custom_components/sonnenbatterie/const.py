import logging
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.data_entry_flow import section
from homeassistant.const import (
    CONF_PASSWORD,
    CONF_USERNAME,
    CONF_IP_ADDRESS,
    CONF_API_TOKEN,
    CONF_PORT,
    CONF_MODEL,
    CONF_DEVICE_ID,
)
from homeassistant.components.sensor import PLATFORM_SCHEMA

LOGGER = logging.getLogger(__package__)

DOMAIN = "sonnenbatterie"
DEFAULT_SCAN_INTERVAL = 10

CONFIG_SCHEMA_A = vol.Schema(
    {
        vol.Required(CONF_USERNAME): vol.In(["User", "Installer"]),
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Required(CONF_IP_ADDRESS): cv.string,
    }
)

SCHEMA_B_DICT =  {
#   vol.Optional(CONF_USERNAME, default='*api_token*'): str,
    vol.Required(CONF_IP_ADDRESS): cv.string,
    vol.Required(CONF_PORT): cv.string,
    "options": section(
        vol.Schema(
            {
                vol.Required("Use API Token", default=True): bool,
                vol.Required("Enable Debug", default=True): bool,
            }
        ),
        # Whether or not the section is initially collapsed (default = False)
        {"collapsed": False},
    ),
    vol.Required(CONF_API_TOKEN): cv.string,
    vol.Required(CONF_MODEL): cv.string,
    vol.Required(CONF_DEVICE_ID): cv.string,
}

CONFIG_SCHEMA_B = vol.Schema(SCHEMA_B_DICT)
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(SCHEMA_B_DICT)

# CONFIG_SCHEMA = vol.Schema(
#     {DOMAIN: CONFIG_SCHEMA_A},
#     extra=vol.ALLOW_EXTRA,
# )

# CONFIG_B_SCHEMA = vol.Schema(
#     {DOMAIN: CONFIG_SCHEMA_B},
#     extra=vol.ALLOW_EXTRA,
# )

ATTR_SONNEN_DEBUG = "sonnenbatterie_debug"
DEFAULT_SONNEN_DEBUG = False
PLATFORMS = ["sensor"]

def flatten_obj(prefix, seperator, obj):
    result = {}
    for field in obj:
        val = obj[field]
        val_prefix = prefix + seperator + field
        if type(val) is dict:
            sub = flatten_obj(val_prefix, seperator, val)
            result.update(sub)
        else:
            result[val_prefix] = val
    return result
