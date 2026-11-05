"""Static checks that do not require a running Home Assistant instance."""
import ast
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "custom_components" / "riello_pv_modbus"

def test_syntax_and_json():
    for path in COMPONENT.rglob("*.py"):
        ast.parse(path.read_text(encoding="utf-8"))
    for path in COMPONENT.rglob("*.json"):
        json.loads(path.read_text(encoding="utf-8"))

def test_no_private_network_literals():
    for path in COMPONENT.rglob("*"):
        if path.is_file() and path.suffix in (".py", ".json"):
            content = path.read_text(encoding="utf-8")
            assert "192.168." not in content
            assert "172.30.33." not in content
