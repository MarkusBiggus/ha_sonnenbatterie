"""sonnenbatterie sensor platform."""

from collections.abc import Callable
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
from homeassistant.components.sensor import (
    SensorEntity,
)
from homeassistant.helpers.typing import (
    StateType,
    ConfigType,
    DiscoveryInfoType,
)
from homeassistant.core import callback
from homeassistant import config_entries, core
from .coordinator import SonnenBatterieCoordinator
from sonnenbatterie import sonnenbatterie
from .const import (
    CONF_PASSWORD,
    CONF_USERNAME,
    CONF_IP_ADDRESS,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    CONF_API_TOKEN,
    ATTR_SONNEN_DEBUG,
    DOMAIN,
    LOGGER,
    logging,
    PLATFORM_SCHEMA,
)
from .sensor_list import (
    SonnenbatterieSensorEntityDescription,
    SENSORS,
    generate_powermeter_sensors,
)

_LOGGER = logging.getLogger(__name__)


async def async_unload_entry(hass, entry):
    """Unload a config entry."""
    ## we dont have anything special going on.. unload should just work, right?
    ##bridge = hass.data[DOMAIN].pop(entry.data['host'])
    return

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the sensor platform."""
    LOGGER.info("SETUP_ENTRY")
    # await async_setup_reload_service(hass, DOMAIN, PLATFORMS)
    username = config_entry.data.get(CONF_USERNAME)
    password = config_entry.data.get(CONF_PASSWORD, None)
    api_token = config_entry.data.get(CONF_API_TOKEN, None)
    ip_address = config_entry.data.get(CONF_IP_ADDRESS)
    ip_port = config_entry.data.get(CONF_PORT, '80')
    update_interval_seconds = config_entry.options.get(CONF_SCAN_INTERVAL, 15)
    debug_mode = config_entry.options.get(ATTR_SONNEN_DEBUG)

    def _internal_setup(_username, _password, _ip_address):
        return sonnenbatterie(_username, _password, _ip_address)

    def _internal_setup_v2(_apitoken, _ipaddress, _ipport):
        return sonnenbatterie(_apitoken, _ipaddress, _ipport) #API V2

    if api_token is not None:
        sonnenInst = await hass.async_add_executor_job(
            _internal_setup_v2, api_token, ip_address, ip_port
        )
    else:
        sonnenInst = await hass.async_add_executor_job(
            _internal_setup, username, password, ip_address
        )
    update_interval_seconds = update_interval_seconds or 1
    LOGGER.info("{0} - UPDATEINTERVAL: {1}".format(DOMAIN, update_interval_seconds))

    """ The Coordinator is called from HA for updates from API """
    coordinator = SonnenBatterieCoordinator(
        hass,
        sonnenInst,
        update_interval_seconds,
        ip_address,
        debug_mode,
        config_entry.entry_id,
    )

    await coordinator.async_config_entry_first_refresh()

    async_add_entities(
        SonnenbatterieSensor(coordinator=coordinator, entity_description=description)
        for description in SENSORS
        if description.value_fn(coordinator=coordinator) is not None
    )

    async_add_entities(
        SonnenbatterieSensor(coordinator=coordinator, entity_description=description)
        for description in generate_powermeter_sensors(_coordinator=coordinator)
    )

    LOGGER.info("Init done")
    return True

async def async_setup_platform(
    hass: core.HomeAssistant,
    config: ConfigType,
    async_add_entities: Callable,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the sensor platform."""
    sensors = [SonnenbatterieSensor(entity) for entity in SENSORS]
    async_add_entities(sensors, update_before_add=True)

class SonnenbatterieSensor(CoordinatorEntity[SonnenBatterieCoordinator], SensorEntity):
    """Represent an SonnenBatterie sensor."""

    entity_description: SonnenbatterieSensorEntityDescription
    _attr_should_poll = False
    _attr_has_entity_name = True
    _attr_suggested_display_precision = 0

    def __init__(
        self,
        coordinator: SonnenBatterieCoordinator,
        entity_description: SonnenbatterieSensorEntityDescription,
    ) -> None:
        super().__init__(coordinator=coordinator)
        self.coordinator = coordinator
        self.entity_description = entity_description

        self._attr_device_info = coordinator.device_info
        self._attr_translation_key = (
            tkey
            if (tkey := entity_description.translation_key)
            else entity_description.key
        )
        if precision := entity_description.suggested_display_precision:
            self._attr_suggested_display_precision = precision

        self.entity_id = f"sensor.sonnenbatterie_{self.coordinator.serial}_{self.entity_description.key}"

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        # return f"{self.coordinator.serial}-{self.entity_description.key}"

        # legacy support / prevent breaking changes
        key = self.entity_description.legacy_key or self.entity_description.key
        return f"sensor.sonnenbatterie_{self.coordinator.serial}_{key}"

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        return self.entity_description.value_fn(self.coordinator)

    # async def async_update(self) -> None:
    #     """Update all sensors."""
    #     try:
    #         self.coordinator.sbInst.get_update()
    #     except (sonnenbatterie.BatterieError):
    #         self._available = False
    #         _LOGGER.exception(
    #             "Error retrieving data from Sonnen for sensor %s", self.name
    #         )