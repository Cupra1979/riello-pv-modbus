# Riello PV Modbus — Home Assistant custom integration

Read-only local Modbus TCP integration for **Riello PV RS 3.0** solar inverter.

> Community project, not affiliated with Riello. The register map has been field-verified on **one PV RS 3.0 installation** using Home Assistant Modbus YAML since August 2026. This Python integration is a new implementation and **has not yet been field-tested**. The first public version is **v1.0.0-rc1 (pre-release)**. Automated checks, including simulated Home Assistant configuration and sensor tests, pass, but this Python integration has **not** been tested on a physical inverter.

## Sensors

Eight direct registers: AC voltage, AC current, AC power, grid frequency, PV voltage, PV current, inverter temperature and total generated energy. Three calculated values: DC power, inverter efficiency and losses. The integration creates one HA device with 11 sensors.

## Installation

### Via HACS (custom repository)

1. Add this repository as a **custom integration repository**.
2. Download **Riello PV Modbus**.
3. Restart Home Assistant if requested.
4. Settings → Devices & services → Add integration → **Riello PV Modbus**.
5. Enter your inverter's own IP/hostname, TCP port (typically **502**) and Modbus slave ID (typically **1**).

### Manual

Copy `custom_components/riello_pv_modbus` into your HA config directory's `custom_components` folder, restart HA, then add from Integrations.

## Settings and privacy

No local IP, serial number, username, token or cloud endpoint is hard-coded. The user supplies network parameters in the config flow. No telemetry and no write-register operations. Only the active inverter's connection settings are stored by HA in its private config-entry storage.

Options permit an update interval between **10–300 seconds**, default 30 seconds. Polling reads eight registers separately to reproduce the proven YAML behavior.

## Homey

Homey may import the resulting HA sensors through its Home Assistant app, depending on Homey app/device support. No special Homey dependency is required.

## Testing and existing Home Assistant installations

**A second Home Assistant instance is not required to install this pre-release.** The repository is checked with automated Modbus simulations, Home Assistant integration tests, hassfest and HACS validation. These checks do not replace field testing on a real inverter; this release is intended for voluntary early adopters.

On a Home Assistant system that already reads the same inverter through Modbus YAML, **do not configure both implementations to poll the inverter at the same time**. Preserve a full backup before switching. Existing dashboards, Energy statistics and Homey connections may depend on your current entity IDs and will not automatically transfer to the new integration.

If you want to keep a working setup untouched, **do not install or configure the new integration on it**. You can continue using the YAML sensors indefinitely. Anyone choosing to switch can follow the instructions below.

## Migrating from Modbus YAML / Device Tools

1. Make a Home Assistant backup and record the existing entity IDs, Energy dashboard source, Device Tools association and Homey automations.
2. Install the custom integration via HACS, but do not configure it yet.
3. Disable the existing Riello Modbus polling and its dependent template sensors; then restart Home Assistant. Make sure unrelated Modbus devices remain configured.
4. Add **Riello PV Modbus** from Settings → Devices & services with your own inverter host, port and slave ID. Confirm all sensors display plausible values.
5. Update dashboard cards, Energy source and Homey references to the new entity IDs, as required. Historical statistics are **not automatically migrated**.
6. Only remove obsolete virtual-device associations after verifying the replacement and keeping a rollback path.

**Note:** The configuration flow checks live communication with the inverter. If the Wi-Fi/Modbus interface is offline at night, initial onboarding may fail; retry while the inverter is reachable. After setup, interruptions mark sensors unavailable and polling resumes when communication returns.

## Automated validation

GitHub Actions runs the read-only adapter tests, a simulated Home Assistant config-flow and 11-sensor lifecycle test, hassfest and HACS checks. No tests contact a private inverter or home network. To run the protocol-only tests locally, execute `python -m unittest discover -s tests -p "test_modbus_offline.py" -v` from the repository root.

## Register map

| Address | Data | Scale | Metric |
| --- | --- | --- | --- |
| 4097 | uint16 | 0.1 | AC voltage V |
| 4098 | uint16 | 0.01 | AC current A |
| 4100 | uint16 | 0.1 | AC power W |
| 4101 | uint16 | 0.01 | Grid frequency Hz |
| 4112 | uint16 | 0.1 | PV voltage V |
| 4113 | uint16 | 0.01 | PV current A |
| 4124 | uint16 | 1 | Temperature °C |
| 4129 | uint32, high word first | 1 | Lifetime generation kWh |

Values are read using function code 03 (holding registers). This integration **never writes registers**. Derived DC power = PV volts × PV amps; efficiency = AC/DC ×100% when DC > 50 W (else zero); losses = max(DC − AC, 0).

## Known limitations

- Verified register layout: PV RS 3.0 only. Other models might differ.
- User must have a functioning Wi-Fi/Modbus TCP interface reachable from HA.
- Inverter offline at night results in unavailable sensors rather than a zero reading.
- No daily energy register, device error codes, alarm registers or write controls.
- `total_energy` should be independently verified against the inverter before inclusion in long-term Energy Dashboard statistics.

## Release status

- Automated protocol, simulated Home Assistant, hassfest and HACS checks have passed.
- The real-world Modbus register map is verified for **PV RS 3.0** through the original YAML setup; this Python implementation still needs independent live-hardware validation.
- Report issues and results via [GitHub Issues](https://github.com/Cupra1979/riello-pv-modbus/issues).
- This project is a community integration; it is not affiliated with or endorsed by Riello.

## Origins

This project contains original integration scaffolding and read logic based on field-verified register measurements. The earlier investigation was informed by [Riello-RSTool](https://github.com/Pierluigi2497/Riello-RSTool); **no source files are copied from that repository**. Check its license before incorporating its code.
