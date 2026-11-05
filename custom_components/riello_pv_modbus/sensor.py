"""Sensors for Riello PV Modbus."""
from __future__ import annotations
from dataclasses import dataclass
from homeassistant.components.sensor import SensorEntity, SensorEntityDescription, SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfElectricCurrent, UnitOfElectricPotential, UnitOfEnergy, UnitOfFrequency, UnitOfPower, UnitOfTemperature, PERCENTAGE
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

@dataclass(frozen=True, kw_only=True)
class RielloSensorDescription(SensorEntityDescription):
    decimals: int = 0

SENSORS = (
    RielloSensorDescription(key="ac_voltage", translation_key="ac_voltage", native_unit_of_measurement=UnitOfElectricPotential.VOLT, device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT, suggested_display_precision=1),
    RielloSensorDescription(key="ac_current", translation_key="ac_current", native_unit_of_measurement=UnitOfElectricCurrent.AMPERE, device_class=SensorDeviceClass.CURRENT, state_class=SensorStateClass.MEASUREMENT, suggested_display_precision=2),
    RielloSensorDescription(key="ac_power", translation_key="ac_power", native_unit_of_measurement=UnitOfPower.WATT, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT, suggested_display_precision=0),
    RielloSensorDescription(key="frequency", translation_key="frequency", native_unit_of_measurement=UnitOfFrequency.HERTZ, device_class=SensorDeviceClass.FREQUENCY, state_class=SensorStateClass.MEASUREMENT, suggested_display_precision=2),
    RielloSensorDescription(key="pv_voltage", translation_key="pv_voltage", native_unit_of_measurement=UnitOfElectricPotential.VOLT, device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT, suggested_display_precision=1),
    RielloSensorDescription(key="pv_current", translation_key="pv_current", native_unit_of_measurement=UnitOfElectricCurrent.AMPERE, device_class=SensorDeviceClass.CURRENT, state_class=SensorStateClass.MEASUREMENT, suggested_display_precision=2),
    RielloSensorDescription(key="temperature", translation_key="temperature", native_unit_of_measurement=UnitOfTemperature.CELSIUS, device_class=SensorDeviceClass.TEMPERATURE, state_class=SensorStateClass.MEASUREMENT, suggested_display_precision=0),
    RielloSensorDescription(key="total_energy", translation_key="total_energy", native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR, device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL_INCREASING, suggested_display_precision=0),
    RielloSensorDescription(key="dc_power", translation_key="dc_power", native_unit_of_measurement=UnitOfPower.WATT, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT, suggested_display_precision=0, icon="mdi:solar-power"),
    RielloSensorDescription(key="efficiency", translation_key="efficiency", native_unit_of_measurement=PERCENTAGE, state_class=SensorStateClass.MEASUREMENT, suggested_display_precision=1, icon="mdi:gauge"),
    RielloSensorDescription(key="losses", translation_key="losses", native_unit_of_measurement=UnitOfPower.WATT, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT, suggested_display_precision=0, icon="mdi:heat-wave"),
)

async def async_setup_entry(hass, entry, async_add_entities) -> None:
    coordinator = entry.runtime_data
    async_add_entities(RielloSensor(coordinator, description) for description in SENSORS)

class RielloSensor(CoordinatorEntity, SensorEntity):
    """A single metric exposed by the configured inverter."""
    _attr_has_entity_name = True

    def __init__(self, coordinator, description: RielloSensorDescription) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        entry = coordinator.entry
        device_key = f"{entry.data['host']}:{entry.data['port']}:{entry.data['unit_id']}"
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_key)},
            name=f"Riello {entry.data['model']}",
            manufacturer="Riello",
            model=entry.data['model'],
        )

    @property
    def native_value(self):
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get(self.entity_description.key)
