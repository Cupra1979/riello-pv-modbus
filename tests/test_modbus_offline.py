"""Offline contract tests: do not contact any physical inverter or LAN."""
import asyncio
import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch

BASE = Path(__file__).resolve().parents[1] / 'custom_components' / 'riello_pv_modbus'

class FakeResponse:
    def __init__(self, registers, failed=False):
        self.registers = registers
        self.failed = failed
    def isError(self):
        return self.failed

class FakeAsyncModbusTcpClient:
    last = None
    fail_at = None
    offline = False
    def __init__(self, host, *, port, timeout, retries):
        self.host, self.port, self.timeout, self.retries = host, port, timeout, retries
        self.connected = not self.offline
        self.calls = []
        type(self).last = self
    async def __aenter__(self):
        return self
    async def __aexit__(self, *args):
        return False
    async def read_holding_registers(self, address, *, count, device_id):
        self.calls.append((address, count, device_id))
        if self.fail_at == address:
            return FakeResponse([], True)
        raw = {
            4097: [2430], 4098: [680], 4100: [15240], 4101: [5000],
            4112: [2060], 4113: [760], 4124: [50], 4129: [0, 12846],
        }[address]
        return FakeResponse(raw)

# Load the production read-only adapter without requiring Home Assistant or
# PyModbus to be installed, and without importing the integration package.
def load_adapter():
    pkg_name = 'riello_pv_modbus_offline'
    pkg = types.ModuleType(pkg_name)
    pkg.__path__ = [str(BASE)]
    pm = types.ModuleType('pymodbus')
    pm_client = types.ModuleType('pymodbus.client')
    pm_exceptions = types.ModuleType('pymodbus.exceptions')
    pm_client.AsyncModbusTcpClient = FakeAsyncModbusTcpClient
    pm_exceptions.ModbusException = type('ModbusException', (Exception,), {})
    sys.modules.update({pkg_name: pkg, 'pymodbus': pm,
                        'pymodbus.client': pm_client,
                        'pymodbus.exceptions': pm_exceptions})
    for name in ('const', 'modbus_client'):
        spec = importlib.util.spec_from_file_location(f'{pkg_name}.{name}', BASE / f'{name}.py')
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
    return sys.modules[f'{pkg_name}.modbus_client']

ADAPTER = load_adapter()

class OfflineTests(unittest.TestCase):
    def setUp(self):
        FakeAsyncModbusTcpClient.fail_at = None
        FakeAsyncModbusTcpClient.offline = False
    def test_reading_and_calculated_values(self):
        values = asyncio.run(ADAPTER.async_read_inverter('example.invalid', 1502, 3))
        self.assertEqual(len(values), 11)
        self.assertEqual(values['ac_voltage'], 243.0)
        self.assertEqual(values['ac_current'], 6.8)
        self.assertEqual(values['ac_power'], 1524.0)
        self.assertEqual(values['frequency'], 50.0)
        self.assertEqual(values['pv_voltage'], 206.0)
        self.assertEqual(values['pv_current'], 7.6)
        self.assertEqual(values['total_energy'], 12846)
        self.assertEqual(values['dc_power'], 1566)
        self.assertEqual(values['efficiency'], 97.3)
        self.assertEqual(values['losses'], 42)
        self.assertEqual(FakeAsyncModbusTcpClient.last.host, 'example.invalid')
        self.assertEqual(FakeAsyncModbusTcpClient.last.port, 1502)
        self.assertEqual(len(FakeAsyncModbusTcpClient.last.calls), 8)
        self.assertTrue(all(call[2] == 3 for call in FakeAsyncModbusTcpClient.last.calls))
        self.assertIn((4129, 2, 3), FakeAsyncModbusTcpClient.last.calls)
    def test_connection_offline(self):
        FakeAsyncModbusTcpClient.offline = True
        with self.assertRaises(ADAPTER.RielloCommunicationError):
            asyncio.run(ADAPTER.async_read_inverter('example.invalid', 502, 1))
    def test_bad_register_response(self):
        FakeAsyncModbusTcpClient.fail_at = 4112
        with self.assertRaises(ADAPTER.RielloCommunicationError):
            asyncio.run(ADAPTER.async_read_inverter('example.invalid', 502, 1))
    def test_recovery_next_cycle(self):
        FakeAsyncModbusTcpClient.offline = True
        with self.assertRaises(ADAPTER.RielloCommunicationError):
            asyncio.run(ADAPTER.async_read_inverter('example.invalid', 502, 1))
        FakeAsyncModbusTcpClient.offline = False
        self.assertEqual(asyncio.run(ADAPTER.async_read_inverter('example.invalid', 502, 1))['total_energy'], 12846)
    def test_no_write_calls_in_adapter(self):
        code = (BASE / 'modbus_client.py').read_text()
        self.assertNotIn('client.write_', code)

if __name__ == '__main__':
    unittest.main()
