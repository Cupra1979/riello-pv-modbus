"""Run real Home Assistant config-flow and sensor lifecycle against a simulated inverter.

No network operations or connection to any physical Riello inverter.
"""
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from pytest_homeassistant_custom_component.common import MockConfigEntry

DOMAIN = "riello_pv_modbus"
DATA = {
    "ac_voltage": 243.0, "ac_current": 6.8, "ac_power": 1524.0,
    "frequency": 50.0, "pv_voltage": 206.0, "pv_current": 7.6,
    "temperature": 50, "total_energy": 12846, "dc_power": 1566,
    "efficiency": 97.3, "losses": 42,
}
CONFIG = {CONF_HOST: "192.0.2.10", CONF_PORT: 502, "unit_id": 1, "model": "PV RS 3.0"}


@pytest.mark.asyncio
async def test_config_flow_creates_entry(hass, enable_custom_integrations):
    with patch("custom_components.riello_pv_modbus.config_flow.async_read_inverter",
               new_callable=AsyncMock, return_value=DATA):
        result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})
        assert result["type"] == config_entries.FlowResultType.FORM
        result = await hass.config_entries.flow.async_configure(result["flow_id"], user_input=CONFIG)
    assert result["type"] == config_entries.FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_HOST] == "192.0.2.10"
    assert result["data"]["unit_id"] == 1


@pytest.mark.asyncio
async def test_setup_creates_eleven_sensors_and_offline_recovery(hass, enable_custom_integrations):
    entry = MockConfigEntry(domain=DOMAIN, data=CONFIG, unique_id="192.0.2.10:502:1")
    entry.add_to_hass(hass)
    with patch("custom_components.riello_pv_modbus.coordinator.async_read_inverter",
               new_callable=AsyncMock, return_value=DATA) as read:
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        registry = hass.data["entity_registry"] if False else None
        from homeassistant.helpers import entity_registry as er
        entities = er.async_entries_for_config_entry(er.async_get(hass), entry.entry_id)
        assert len(entities) == 11
        names = {entity.unique_id.split("_")[-1] for entity in entities}
        assert all(entity.entity_id.startswith("sensor.") for entity in entities)
        assert any(entity.entity_id.endswith("total_energy") for entity in entities)
        coordinator = entry.runtime_data
        assert coordinator.last_update_success
        assert len(coordinator.data) == 11
        read.side_effect = OSError("simulated disconnection")
        await coordinator.async_refresh()
        assert not coordinator.last_update_success
        read.side_effect = None
        read.return_value = DATA
        await coordinator.async_refresh()
        assert coordinator.last_update_success
        assert await hass.config_entries.async_unload(entry.entry_id)
