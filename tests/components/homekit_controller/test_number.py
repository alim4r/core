"""Basic checks for HomeKit sensor."""
from aiohomekit.model.characteristics import CharacteristicsTypes
from aiohomekit.model.services import ServicesTypes

from tests.components.homekit_controller.common import Helper, setup_test_component


def create_switch_with_spray_level(accessory):
    """Define battery level characteristics."""
    service = accessory.add_service(ServicesTypes.OUTLET)

    spray_level = service.add_char(
        CharacteristicsTypes.Vendor.VOCOLINC_HUMIDIFIER_SPRAY_LEVEL
    )

    spray_level.perms.append("ev")
    spray_level.value = 1
    spray_level.minStep = 1
    spray_level.minValue = 1
    spray_level.maxValue = 5
    spray_level.format = "float"

    cur_state = service.add_char(CharacteristicsTypes.ON)
    cur_state.value = True

    return service


def create_switch_with_ecobee_fan_mode(accessory):
    """Define battery level characteristics."""
    service = accessory.add_service(ServicesTypes.OUTLET)

    ecobee_fan_mode = service.add_char(
        CharacteristicsTypes.Vendor.ECOBEE_FAN_WRITE_SPEED
    )

    ecobee_fan_mode.value = 0
    ecobee_fan_mode.minStep = 1
    ecobee_fan_mode.minValue = 0
    ecobee_fan_mode.maxValue = 100
    ecobee_fan_mode.format = "float"

    cur_state = service.add_char(CharacteristicsTypes.ON)
    cur_state.value = True

    return service


async def test_read_number(hass, utcnow):
    """Test a switch service that has a sensor characteristic is correctly handled."""
    helper = await setup_test_component(hass, create_switch_with_spray_level)

    # Helper will be for the primary entity, which is the outlet. Make a helper for the sensor.
    spray_level = Helper(
        hass,
        "number.testdevice_spray_quantity",
        helper.pairing,
        helper.accessory,
        helper.config_entry,
    )

    state = await spray_level.poll_and_get_state()
    assert state.state == "1"
    assert state.attributes["step"] == 1
    assert state.attributes["min"] == 1
    assert state.attributes["max"] == 5

    state = await spray_level.async_update(
        ServicesTypes.OUTLET,
        {CharacteristicsTypes.Vendor.VOCOLINC_HUMIDIFIER_SPRAY_LEVEL: 5},
    )
    assert state.state == "5"


async def test_write_number(hass, utcnow):
    """Test a switch service that has a sensor characteristic is correctly handled."""
    helper = await setup_test_component(hass, create_switch_with_spray_level)

    # Helper will be for the primary entity, which is the outlet. Make a helper for the sensor.
    spray_level = Helper(
        hass,
        "number.testdevice_spray_quantity",
        helper.pairing,
        helper.accessory,
        helper.config_entry,
    )

    await hass.services.async_call(
        "number",
        "set_value",
        {"entity_id": "number.testdevice_spray_quantity", "value": 5},
        blocking=True,
    )
    spray_level.async_assert_service_values(
        ServicesTypes.OUTLET,
        {CharacteristicsTypes.Vendor.VOCOLINC_HUMIDIFIER_SPRAY_LEVEL: 5},
    )

    await hass.services.async_call(
        "number",
        "set_value",
        {"entity_id": "number.testdevice_spray_quantity", "value": 3},
        blocking=True,
    )
    spray_level.async_assert_service_values(
        ServicesTypes.OUTLET,
        {CharacteristicsTypes.Vendor.VOCOLINC_HUMIDIFIER_SPRAY_LEVEL: 3},
    )


async def test_write_ecobee_fan_mode_number(hass, utcnow):
    """Test a switch service that has a sensor characteristic is correctly handled."""
    helper = await setup_test_component(hass, create_switch_with_ecobee_fan_mode)

    # Helper will be for the primary entity, which is the outlet. Make a helper for the sensor.
    fan_mode = Helper(
        hass,
        "number.testdevice_fan_mode",
        helper.pairing,
        helper.accessory,
        helper.config_entry,
    )

    await hass.services.async_call(
        "number",
        "set_value",
        {"entity_id": "number.testdevice_fan_mode", "value": 1},
        blocking=True,
    )
    fan_mode.async_assert_service_values(
        ServicesTypes.OUTLET,
        {CharacteristicsTypes.Vendor.ECOBEE_FAN_WRITE_SPEED: 1},
    )

    await hass.services.async_call(
        "number",
        "set_value",
        {"entity_id": "number.testdevice_fan_mode", "value": 2},
        blocking=True,
    )
    fan_mode.async_assert_service_values(
        ServicesTypes.OUTLET,
        {CharacteristicsTypes.Vendor.ECOBEE_FAN_WRITE_SPEED: 2},
    )

    await hass.services.async_call(
        "number",
        "set_value",
        {"entity_id": "number.testdevice_fan_mode", "value": 99},
        blocking=True,
    )
    fan_mode.async_assert_service_values(
        ServicesTypes.OUTLET,
        {CharacteristicsTypes.Vendor.ECOBEE_FAN_WRITE_SPEED: 99},
    )

    await hass.services.async_call(
        "number",
        "set_value",
        {"entity_id": "number.testdevice_fan_mode", "value": 100},
        blocking=True,
    )
    fan_mode.async_assert_service_values(
        ServicesTypes.OUTLET,
        {CharacteristicsTypes.Vendor.ECOBEE_FAN_WRITE_SPEED: 100},
    )

    await hass.services.async_call(
        "number",
        "set_value",
        {"entity_id": "number.testdevice_fan_mode", "value": 0},
        blocking=True,
    )
    fan_mode.async_assert_service_values(
        ServicesTypes.OUTLET,
        {CharacteristicsTypes.Vendor.ECOBEE_FAN_WRITE_SPEED: 0},
    )
