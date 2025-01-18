"""Fixture to load batterie charging responses
    using all sync methods called from async tests using asyncio.run_in_executor
    to emulate ha component calls
"""
import logging
import pytest
import asyncio
from collections.abc import (
    Callable,
)

from sonnen_api_v2 import Batterie
#from sonnen_api_v2.sonnen import Sonnen as Batterie, BatterieError

from . mock_sonnenbatterie_v2_charging import __mock_status_charging, __mock_latest_charging, __mock_configurations, __mock_battery, __mock_powermeter, __mock_inverter

LOGGER_NAME = "sonnenapiv2"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

@pytest.fixture(name="battery_charging")
async def fixture_battery_charging(mocker) -> Batterie:
    if LOGGER_NAME is not None:
        logging.basicConfig(filename=(f'/tests/logs/{LOGGER_NAME}.log'), level=logging.DEBUG)
        logger = logging.getLogger(LOGGER_NAME)
        logger.info('Sonnen mock data battery_charging_asyncio test.')

    # Can't mock a coroutine!
    mocker.patch.object(Batterie, "fetch_status", __mock_status_charging)
    mocker.patch.object(Batterie, "fetch_latest_details", __mock_latest_charging)
    mocker.patch.object(Batterie, "fetch_configurations", __mock_configurations)
    mocker.patch.object(Batterie, "fetch_battery_status", __mock_battery)
    mocker.patch.object(Batterie, "fetch_powermeter", __mock_powermeter)
    mocker.patch.object(Batterie, "fetch_inverter", __mock_inverter)

    def async_add_executor_job[*_Ts, _T](
        target: Callable[[*_Ts], _T], *args: *_Ts
        ) -> asyncio.Future[_T]:
        """Add an executor job from within the event loop."""
        loop = asyncio.get_running_loop()
        task = loop.run_in_executor(None, target, *args)
    #    print (f'task type: {type(task)}')
        return task

    def _sync_update(battery_charging: Batterie) -> bool:
        """Coroutine to sync fetch"""
        return battery_charging.sync_get_update()

    battery_charging = Batterie('fakeToken', 'fakeHost')

    success = await async_add_executor_job(
        _sync_update, battery_charging
#        target = _sync_update, args = [battery_charging]
    )
    assert success is not False

    return battery_charging
