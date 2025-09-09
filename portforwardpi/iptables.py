"""iptables helpers for PortForwardPi."""

from __future__ import annotations

import subprocess
from typing import Dict, Any


Config = Dict[str, Any]


def apply_rules(config: Config) -> None:
    """Apply *config* rules using iptables.

    ``config`` expects keys ``forwards``, ``allow_ips``, ``block_ips``,
    ``allow_countries`` and ``block_countries``. Port forwarding rules are
    applied to the ``PREROUTING`` chain in the ``nat`` table. Filtering rules
    are applied through a dedicated ``PORTFORWARDPI_FILTER`` chain hooked into
    ``INPUT``.
    """
    # Flush forwarding rules
    subprocess.run(["iptables", "-t", "nat", "-F", "PREROUTING"], check=True)
    for rule in config["forwards"]:
        cmd = [
            "iptables",
            "-t",
            "nat",
            "-A",
            "PREROUTING",
            "-p",
            "tcp",
            "--dport",
            str(rule["local_port"]),
            "-j",
            "DNAT",
            "--to-destination",
            f"{rule['remote_ip']}:{rule['remote_port']}",
        ]
        subprocess.run(cmd, check=True)

    chain = "PORTFORWARDPI_FILTER"
    # Prepare custom chain; ignore errors if chain exists or hook already added
    subprocess.run(["iptables", "-F", chain], check=False)
    subprocess.run(["iptables", "-N", chain], check=False)
    subprocess.run(["iptables", "-C", "INPUT", "-j", chain], check=False)
    subprocess.run(["iptables", "-I", "INPUT", "1", "-j", chain], check=False)

    # Allow rules
    for ip in config["allow_ips"]:
        subprocess.run(["iptables", "-A", chain, "-s", ip, "-j", "ACCEPT"], check=True)
    for cc in config["allow_countries"]:
        subprocess.run(
            ["iptables", "-A", chain, "-m", "geoip", "--src-cc", cc, "-j", "ACCEPT"],
            check=True,
        )

    # Block rules
    for ip in config["block_ips"]:
        subprocess.run(["iptables", "-A", chain, "-s", ip, "-j", "DROP"], check=True)
    for cc in config["block_countries"]:
        subprocess.run(
            ["iptables", "-A", chain, "-m", "geoip", "--src-cc", cc, "-j", "DROP"],
            check=True,
        )

    # Return to INPUT chain
    subprocess.run(["iptables", "-A", chain, "-j", "RETURN"], check=True)
