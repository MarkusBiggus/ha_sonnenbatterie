import logging
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.selector import selector
from homeassistant.data_entry_flow import section
from homeassistant.const import (
    Platform,
    CONF_PASSWORD,
    CONF_USERNAME,
    CONF_IP_ADDRESS,
    CONF_API_TOKEN,
    CONF_PORT,
    CONF_MODEL,
    CONF_DEVICE_ID,
)
#from homeassistant.components.sensor import PLATFORM_SCHEMA

LOGGER = logging.getLogger(__package__)

DOMAIN = "sonnenbatterie"
MANUFACTURER = "Sonnen GmbH"

DEFAULT_SCAN_INTERVAL = 10

CONFIG_SCHEMA_BASE = vol.Schema(
    {
    vol.Required(CONF_IP_ADDRESS): cv.string,
    vol.Required(CONF_PORT): cv.string,
    vol.Required("use_token", default=True): bool,
    "options": section(
        vol.Schema(
            {
                vol.Required("SCAN_INTERVAL", default=DEFAULT_SCAN_INTERVAL): int,
                vol.Required("SONNEN_DEBUG", default=True): bool,
            }
        ),
        # Whether or not the section is initially collapsed (default = False)
        {"collapsed": False},
        )
    }
)

CONFIG_SCHEMA_PASSWORD = CONFIG_SCHEMA_BASE.extend(
    {
    vol.Required(CONF_USERNAME): selector(
        {
            "select": {
                "options": ["User", "Installer"],
            }
        }
    ),
    vol.Required(CONF_PASSWORD): cv.string,
    }
)

CONFIG_SCHEMA_TOKEN = CONFIG_SCHEMA_BASE.extend(
    {
    vol.Required(CONF_API_TOKEN): cv.string,
    vol.Required(CONF_MODEL): cv.string,
    vol.Required(CONF_DEVICE_ID): cv.string,
    }
)

#PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(SCHEMA_B_DICT)


ATTR_SONNEN_DEBUG = "sonnenbatterie_debug"
DEFAULT_SONNEN_DEBUG = False
PLATFORMS = [Platform.SENSOR]

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
