"""Read-only Modbus TCP adapter for verified Riello PV RS 3.0 registers."""
from __future__ import annotations
from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException
from .const import REGISTERS

class RielloCommunicationError(Exception):
    """A Modbus read failed."""

async def async_read_inverter(host: str, port: int, unit_id: int) -> dict[str, float]:
    """Read documented registers in separate requests, matching tested YAML configuration.

    No registers are ever written. A connection is created for each polling cycle
    to allow reliable recovery when the inverter's Wi-Fi module reconnects.
    """
    values: dict[str, float] = {}
    try:
        async with AsyncModbusTcpClient(host, port=port, timeout=5, retries=1) as client:
            if not client.connected:
                raise RielloCommunicationError("Unable to connect to inverter")
            for name, (address, count, scale) in REGISTERS.items():
                # PyModbus 3.11+ uses device_id, not the legacy slave keyword.
                reply = await client.read_holding_registers(
                    address, count=count, device_id=unit_id
                )
                if reply.isError() or len(reply.registers) != count:
                    raise RielloCommunicationError(f"Invalid response for {name}")
                raw = reply.registers[0]
                if count == 2:
                    raw = (reply.registers[0] << 16) | reply.registers[1]
                values[name] = round(raw * scale, 4)
    except RielloCommunicationError:
        raise
    except (OSError, TimeoutError, ValueError, AttributeError, ModbusException) as err:
        raise RielloCommunicationError("Modbus communication failed") from err
    # Derived figures are calculated from values of the same polling cycle.
    dc = values["pv_voltage"] * values["pv_current"]
    ac = values["ac_power"]
    values["dc_power"] = round(dc)
    values["efficiency"] = round(100 * ac / dc, 1) if dc > 50 else 0
    values["losses"] = round(max(dc - ac, 0))
    return values
