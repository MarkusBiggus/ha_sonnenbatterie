"""The SonnenBatterie integration."""

from .const import DOMAIN, LOGGER
import json

from homeassistant.const import (
    CONF_SCAN_INTERVAL,
    Platform
)
from homeassistant.config_entries import ConfigEntry
from .coordinator import SonnenBatterieCoordinator

PLATFORMS = [Platform.SENSOR]

type SonnenbatterieConfigEntry = ConfigEntry[SonnenBatterieCoordinator]

async def async_setup(hass, config):
    hass.data.setdefault(DOMAIN, {})
    """Set up a skeleton component."""
    # if DOMAIN not in config:
    #    hass.states.async_set('sonnenbatterie.test', 'Works!')
    #    return True

    # hass.states.async_set('sonnenbatterie.test', 'Works!')
    return True


async def async_setup_entry(hass, config_entry: SonnenbatterieConfigEntry) -> bool:
    LOGGER.info("SonnenbatterieConfigEntry: " + json.dumps(dict(config_entry.data)))

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)
    config_entry.add_update_listener(update_listener)
    config_entry.async_on_unload(config_entry.add_update_listener(async_reload_entry))
    return True


async def async_reload_entry(hass, entry):
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


async def update_listener(hass, entry):
    LOGGER.info("Update listener" + json.dumps(dict(entry.options)))
    hass.data[DOMAIN][entry.entry_id]["monitor"].update_interval_seconds = (
        entry.options.get(CONF_SCAN_INTERVAL)
    )


async def async_unload_entry(hass, config_entry: SonnenbatterieConfigEntry) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_forward_entry_unload(config_entry, PLATFORMS)
