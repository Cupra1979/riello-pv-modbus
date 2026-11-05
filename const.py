"""Constants for the Riello PV Modbus integration."""
from datetime import timedelta
DOMAIN = "riello_pv_modbus"
DEFAULT_PORT = 502
DEFAULT_UNIT = 1
DEFAULT_SCAN_INTERVAL = 30
MIN_SCAN_INTERVAL = 10
MAX_SCAN_INTERVAL = 300
DEFAULT_MODEL = "PV RS 3.0"
CONF_UNIT = "unit_id"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_MODEL = "model"
PLATFORMS = ["sensor"]
REGISTERS = {
    "ac_voltage": (4097, 1, 0.1),
    "ac_current": (4098, 1, 0.01),
    "ac_power": (4100, 1, 0.1),
    "frequency": (4101, 1, 0.01),
    "pv_voltage": (4112, 1, 0.1),
    "pv_current": (4113, 1, 0.01),
    "temperature": (4124, 1, 1),
    "total_energy": (4129, 2, 1),
}
