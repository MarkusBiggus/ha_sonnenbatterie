"""pytest test/test_battery_packages.py -s -v -x
"""
#import datetime
import os
import sys

import logging
import pytest
# import asyncio
# from collections.abc import (
#     Callable,
# )

#import json

#from sonnen_api_v2 import Batterie
from sonnenbatterie import sonnenbatterie


#from .battery_charging_asyncio import fixture_battery_charging
from .battery_charging_coroutine import fixture_battery_charging_ha


LOGGER_NAME = None # "sonnenapiv2" #


logging.getLogger("mock_batterie").setLevel(logging.WARNING)

if LOGGER_NAME is not None:
    filename=f'tests/logs/{LOGGER_NAME}.log'
    logging.basicConfig(filename=filename, level=logging.DEBUG)
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(LOGGER_NAME)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.DEBUG)
    # create file handler which logs debug messages
    fh = logging.FileHandler(filename=filename, mode='a')
    fh.setLevel(logging.DEBUG)
    # console handler display logs messages to console
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    logger.addHandler(fh)
    logger.addHandler(ch)
    logger.info ('Asyncio mock batterie tests')


# ASYNC like ha component
@pytest.mark.asyncio
@pytest.mark.usefixtures("battery_charging_ha")
async def test_batterie_emulator_mocked(battery_charging: sonnenbatterie):
    """test to confirm the sonnen_api_v2 package is installed
        and working in the environment of ha .
        Async method calls sync methods in sonnen_api_v2 using
        asyncio.run_in_executor same as sonnenbatterie custom_component
    """
    #sonnen_api_v2 package tests via emulator
    version = battery_charging.batterie.configuration_de_software # mock_configurations
    status = battery_charging.batterie.system_status # latest_charging
    backup_buffer = battery_charging.batterie.status_backup_buffer # status_charging
    kwh_consumed = battery_charging.batterie.kwh_consumed # mock_powermeter
    cycles = battery_charging.batterie.battery_cycle_count # mock_battery
    PAC_total = battery_charging.batterie.inverter_pac_total # mock_inverter

    print(f'\n\rStatus: {status}  Software Version: {version}   Battery Cycles: {cycles:,}')
    print(f'PAC: {PAC_total:,.2f}W  Consumed: {kwh_consumed:,.2f}  Backup Buffer: {backup_buffer}%')
    assert status == 'OnGrid'
    assert cycles == 30
    assert version == '1.14.5'
    assert PAC_total == -1394.33
    assert backup_buffer == 20
    assert kwh_consumed == 816.5

    total_installed_capacity = battery_charging.batterie.installed_capacity
    batt_reserve_percent = battery_charging.batterie.status_backup_buffer
    total_capacity_raw = battery_charging.batterie.battery_full_charge_capacity_wh
    reserved_capacity = int(
            total_installed_capacity * batt_reserve_percent / 100.0
        )
    remaining_capacity = (
            int(total_capacity_raw * battery_charging.batterie.battery_rsoc) / 100.0
        )
    remaining_capacity_usable = max(
            0, int(remaining_capacity - reserved_capacity))
    print(f'remaining_capacity (raw): {remaining_capacity:,}Wh  remaining_usable (raw): {remaining_capacity_usable:,}Wh')
    print(f'full_charge_capacity (raw): {total_capacity_raw:,}Wh')


# ASYNC like ha component
@pytest.mark.asyncio
@pytest.mark.usefixtures("battery_charging_ha")
async def test_batterie_emulator_ha(battery_charging_ha: sonnenbatterie):
    """sonnenbatterie_api_v2 package: Batterie charging using mock data
        Emulate ha component use - call sync methods asynchronously via asyncio.run_in_executor
    """
    #sonnenbatterie_api_v2 emulater methods
    latestData = {}

    latestData["battery_system"] = await battery_charging_ha.get_batterysystem()
    # async_add_executor_job(
    #         target=battery_charging_ha.get_batterysystem
    #     )
    print(f'battery_system type: {type(latestData["battery_system"])} {latestData["battery_system"]}')

    latestData["status"] = await battery_charging_ha.get_status()
    # async_add_executor_job(self,
    #         target=battery_charging_ha.get_status
    #     )
    print(f'status type: {type(latestData["status"])} {latestData["status"]}')

    batt_module_capacity = int(
        latestData["battery_system"]["battery_system"]["system"][
            "storage_capacity_per_module"
        ]
    )
    batt_module_count = int(latestData["battery_system"]["modules"])
    total_installed_capacity = int(batt_module_count * batt_module_capacity)

    # from sonnenbatterie ha component coordinator
    batt_reserved_factor = 7.0
    latestData["battery_info"] = await battery_charging_ha.get_battery()
    latestData["battery_info"][
        "total_installed_capacity"
    ] = total_installed_capacity = int(batt_module_count * batt_module_capacity)
    latestData["battery_info"]["reserved_capacity"] = reserved_capacity = int(
        total_installed_capacity * (batt_reserved_factor / 100.0)
    )
    latestData["battery_info"]["remaining_capacity"] = remaining_capacity = (
        int(total_installed_capacity * latestData["status"]["RSOC"]) / 100.0
    )
    latestData["battery_info"]["remaining_capacity_usable"] = max(
        0, int(remaining_capacity - reserved_capacity)
    )

    #print(f'battery_info: {latestData["battery_info"]}')
    latestData["powermeter"] = await battery_charging_ha.get_powermeter()
    latestData["inverter"] = await battery_charging_ha.get_inverter()
    latestData["system_data"] = await battery_charging_ha.get_systemdata()

    assert latestData["battery_info"].get('reserved_capacity') == 1400
    assert latestData["system_data"].get('ERP_ArticleName') == 'unknown' #'Power unit Evo IP56'
    assert latestData["powermeter"][1].get('kwh_imported') == 816.5
    assert latestData["inverter"].get('pac_total') == -1394.33

    # every other get method
    login_timeout = battery_charging_ha.get_login_timeout()
    request_connect_timeout = battery_charging_ha.get_request_connect_timeout()
    request_read_timeout = battery_charging_ha.get_request_read_timeout()
    version =  await battery_charging_ha.get_configuration("DE_Software")
    #print(f'login_timeout: {login_timeout}  connect_timeout: {request_connect_timeout}  read_timeout: {request_read_timeout}')
    assert version == '1.14.5'
    assert login_timeout == 120
    assert request_connect_timeout == 60
    assert request_read_timeout == 60
    request_timeouts = battery_charging_ha.set_request_connect_timeout(15)
    assert request_timeouts == (15,60)
    request_timeouts = battery_charging_ha.set_request_read_timeout(25)
    assert request_timeouts == (15,25)

    current_charge_level = await battery_charging_ha.get_current_charge_level()
    operating_mode = battery_charging_ha.get_operating_mode()
    operating_mode_name = battery_charging_ha.get_operating_mode_name()
    battery_reserve = battery_charging_ha.get_battery_reserve()
    #print(f'current_charge_level: {current_charge_level}  operating_mode: {operating_mode}  name: {operating_mode_name}  battery_reserve:{battery_reserve}%')
    assert current_charge_level == 88
    assert operating_mode == 2
    assert operating_mode_name == 'Automatic - Self Consumption'
    assert battery_reserve == 20
    time_of_use_schedule_as_string = await battery_charging_ha.get_time_of_use_schedule_as_string()
    #print(f'TOU: schedule_as_string: {time_of_use_schedule_as_string}  type:{type(time_of_use_schedule_as_string)}')
    assert time_of_use_schedule_as_string == '[]'
    time_of_use_schedule_as_json_objects = await battery_charging_ha.get_time_of_use_schedule_as_json_objects()
    #print(f'TOU: schedule_as_json: {time_of_use_schedule_as_json_objects}  type:{type(time_of_use_schedule_as_json_objects)}')
    assert time_of_use_schedule_as_json_objects == []
    time_of_use_schedule_as_schedule = await battery_charging_ha.get_time_of_use_schedule_as_schedule()
    #print(f'TOU: schedule_as_schedule: {time_of_use_schedule_as_schedule}')
