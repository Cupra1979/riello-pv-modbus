"""User-facing setup for Riello PV Modbus."""
from __future__ import annotations
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from .const import (
    CONF_MODEL, CONF_SCAN_INTERVAL, CONF_UNIT, DEFAULT_MODEL, DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL, DEFAULT_UNIT, DOMAIN, MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
)
from .modbus_client import RielloCommunicationError, async_read_inverter

class RielloPVConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Configure Riello PV Modbus."""
    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        errors = {}
        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            port = user_input[CONF_PORT]
            unit = user_input[CONF_UNIT]
            await self.async_set_unique_id(f"{host}:{port}:{unit}")
            self._abort_if_unique_id_configured()
            try:
                await async_read_inverter(host, port, unit)
            except RielloCommunicationError:
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title=f"Riello {user_input[CONF_MODEL]} ({host})",
                    data={**user_input, CONF_HOST: host},
                )
        schema = vol.Schema({
            vol.Required(CONF_HOST): str,
            vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.All(vol.Coerce(int), vol.Range(min=1, max=65535)),
            vol.Required(CONF_UNIT, default=DEFAULT_UNIT): vol.All(vol.Coerce(int), vol.Range(min=1, max=247)),
            vol.Required(CONF_MODEL, default=DEFAULT_MODEL): vol.In([DEFAULT_MODEL]),
        })
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return RielloOptionsFlow()

class RielloOptionsFlow(config_entries.OptionsFlow):
    """Update polling interval."""
    async def async_step_init(self, user_input=None) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(
                    CONF_SCAN_INTERVAL,
                    default=self.config_entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                ): vol.All(vol.Coerce(int), vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL)),
            }),
        )
