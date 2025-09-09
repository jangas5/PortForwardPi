from unittest.mock import patch

from portforwardpi.iptables import apply_rules


def test_apply_rules_invokes_iptables():
    cfg = {
        "forwards": [{"local_port": 80, "remote_ip": "1.2.3.4", "remote_port": 8080}],
        "allow_ips": ["1.1.1.1"],
        "block_ips": ["2.2.2.2"],
        "allow_countries": ["US"],
        "block_countries": ["CN"],
    }
    with patch("subprocess.run") as run:
        apply_rules(cfg)
        calls = [args[0] for args, kwargs in run.call_args_list]
        assert ["iptables", "-t", "nat", "-F", "PREROUTING"] in calls
        assert [
            "iptables",
            "-t",
            "nat",
            "-A",
            "PREROUTING",
            "-p",
            "tcp",
            "--dport",
            "80",
            "-j",
            "DNAT",
            "--to-destination",
            "1.2.3.4:8080",
        ] in calls
        assert ["iptables", "-A", "PORTFORWARDPI_FILTER", "-s", "1.1.1.1", "-j", "ACCEPT"] in calls
        assert ["iptables", "-A", "PORTFORWARDPI_FILTER", "-s", "2.2.2.2", "-j", "DROP"] in calls
        assert [
            "iptables",
            "-A",
            "PORTFORWARDPI_FILTER",
            "-m",
            "geoip",
            "--src-cc",
            "US",
            "-j",
            "ACCEPT",
        ] in calls
        assert [
            "iptables",
            "-A",
            "PORTFORWARDPI_FILTER",
            "-m",
            "geoip",
            "--src-cc",
            "CN",
            "-j",
            "DROP",
        ] in calls
