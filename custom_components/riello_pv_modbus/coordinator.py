"""Polling coordinator for Riello PV Modbus."""
from __future__ import annotations
from datetime import timedelta
import logging
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import DOMAIN
from .modbus_client import RielloCommunicationError, async_read_inverter

class RielloCoordinator(DataUpdateCoordinator[dict[str, float]]):
    """Single poll for all inverter entities."""

    def __init__(self, hass: HomeAssistant, entry) -> None:
        super().__init__(
            hass,
            logger=logging.getLogger(__name__),
            name=DOMAIN,
            update_interval=timedelta(seconds=entry.options.get('scan_interval', 30)),
            config_entry=entry,
        )
        self.entry = entry

    async def _async_update_data(self) -> dict[str, float]:
        try:
            return await async_read_inverter(
                self.entry.data["host"],
                self.entry.data["port"],
                self.entry.data["unit_id"],
            )
        except RielloCommunicationError as err:
            raise UpdateFailed(str(err)) from err
