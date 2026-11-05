"""Expose the checked-out custom component to Home Assistant's pytest plugin.

The test plugin ships a top-level custom_components package. Extend its path
to include this repository so mocks patch the same modules HA loads.
"""
from pathlib import Path
import custom_components

integration_root = str(Path(__file__).resolve().parents[1] / "custom_components")
if integration_root not in custom_components.__path__:
    custom_components.__path__.append(integration_root)
