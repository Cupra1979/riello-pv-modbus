# Riello PV Modbus — Home Assistant custom integration

Read-only local Modbus TCP integration for **Riello PV RS 3.0** solar inverter.

> Community project, not affiliated with Riello. The register map has been field-verified on **one PV RS 3.0 installation** using Home Assistant Modbus YAML since August 2026. This Python integration is a new implementation and **has not yet been field-tested**. Treat v1.0.0 as a release candidate until validated against a physical inverter.

## Sensors

Eight direct registers: AC voltage, AC current, AC power, grid frequency, PV voltage, PV current, inverter temperature and total generated energy. Three calculated values: DC power, inverter efficiency and losses. The integration creates one HA device with 11 sensors.

## Installation

### Via HACS / Marketplace (when repository is published)

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

## Non-invasive validation (recommended for an existing stable installation)

**Do not install this candidate onto the currently working Home Assistant instance.** The included tests can be run on another computer and never open a real Modbus connection. Run `python -m unittest discover -s tests -p "test_modbus_offline.py" -v` from the repository root. GitHub Actions runs these tests on each commit. These tests cover register decoding, derived calculations, offline errors and recovery on the next polling cycle, but do **not** prove compatibility with a real PV RS 3.0 or the full Home Assistant runtime.

A separate disposable Home Assistant test instance is preferable for any integration installation testing. If available, use a Modbus simulator to test the full integration without contacting the live inverter. A public stable release should only follow that test and a field test volunteered by a separate user; the original installation need never be modified.

## Switching from YAML / Device Tools

**Avoid double polling and duplicate sensor IDs.** Back up your Home Assistant configuration and record entity IDs and dashboards. Disable/remove the old `modbus:` Riello sensor definitions and associated templates after confirming the new entities have valid values. Remove the old virtual Device Tools association only when safe. The new sensor entity IDs may differ from the old ones; update dashboard references, energy source and Homey mappings as needed. **Historical statistics are not automatically migrated.**

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

## Publishing checklist

- GitHub repository references set to `Cupra1979/riello-pv-modbus`.
- Add branded artwork permitted for redistribution, GitHub release and issue templates.
- Local offline protocol adapter tests: **5 passing** (simulated responses only); Python syntax and JSON checks completed.
- Run Home Assistant integration lifecycle tests in a disposable HA instance, `hassfest`, and HACS checks before publication.
- Verify a clean first install, offline recovery, nighttime behavior, Energy dashboard and 24-hour logging with real PV RS 3.0 hardware.
- Run `hassfest`/HACS checks before applying for public catalog listing.

## Origins

This project contains original integration scaffolding and read logic based on field-verified register measurements. The earlier investigation was informed by [Riello-RSTool](https://github.com/Pierluigi2497/Riello-RSTool); **no source files are copied from that repository**. Check its license before incorporating its code.
