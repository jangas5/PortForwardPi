from pathlib import Path

from portforwardpi.config import load_config, save_config, DEFAULT_CONFIG


def test_load_nonexistent(tmp_path: Path):
    path = tmp_path / "config.json"
    assert load_config(path) == DEFAULT_CONFIG


def test_save_and_load(tmp_path: Path):
    path = tmp_path / "config.json"
    data = DEFAULT_CONFIG.copy()
    data["forwards"].append({"local_port": 80, "remote_ip": "1.1.1.1", "remote_port": 8080})
    data["allow_ips"].append("2.2.2.2")
    save_config(path, data)
    assert load_config(path) == data
