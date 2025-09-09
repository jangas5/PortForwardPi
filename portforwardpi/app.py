"""Web application to manage port forwarding rules."""

from __future__ import annotations

from flask import Flask, render_template_string, request, redirect, url_for

from .config import load_config, save_config
from .iptables import apply_rules

app = Flask(__name__)
CONFIG_FILE = "config.json"

# Apply existing rules at startup so configuration persists across restarts.
try:
    apply_rules(load_config(CONFIG_FILE))
except Exception:
    # During testing or without privileges this may fail; ignore the error.
    pass

TEMPLATE = """
<!doctype html>
<title>PortForwardPi</title>
<h1>Port Forward Rules</h1>
<table border="1">
    <tr><th>Index</th><th>Local Port</th><th>Remote IP</th><th>Remote Port</th><th>Action</th></tr>
    {% for idx, rule in enumerate(config.forwards) %}
    <tr>
        <td>{{ idx }}</td>
        <td>{{ rule.local_port }}</td>
        <td>{{ rule.remote_ip }}</td>
        <td>{{ rule.remote_port }}</td>
        <td>
            <form action="{{ url_for('delete_forward', idx=idx) }}" method="post" style="display:inline">
                <button type="submit">Delete</button>
            </form>
        </td>
    </tr>
    {% endfor %}
</table>
<h2>Add Rule</h2>
<form action="{{ url_for('add_forward') }}" method="post">
    Local Port: <input name="local_port" required><br>
    Remote IP: <input name="remote_ip" required><br>
    Remote Port: <input name="remote_port" required><br>
    <button type="submit">Add</button>
</form>

<h1>IP Filters</h1>
<h2>Allowed IPs</h2>
<ul>
{% for idx, ip in enumerate(config.allow_ips) %}
<li>{{ ip }}
    <form action="{{ url_for('delete_allow_ip', idx=idx) }}" method="post" style="display:inline">
        <button type="submit">Delete</button>
    </form>
</li>
{% endfor %}
</ul>
<form action="{{ url_for('add_allow_ip') }}" method="post">
    IP: <input name="value" required>
    <button type="submit">Add</button>
</form>

<h2>Blocked IPs</h2>
<ul>
{% for idx, ip in enumerate(config.block_ips) %}
<li>{{ ip }}
    <form action="{{ url_for('delete_block_ip', idx=idx) }}" method="post" style="display:inline">
        <button type="submit">Delete</button>
    </form>
</li>
{% endfor %}
</ul>
<form action="{{ url_for('add_block_ip') }}" method="post">
    IP: <input name="value" required>
    <button type="submit">Add</button>
</form>

<h1>Country Filters</h1>
<h2>Allowed Countries</h2>
<ul>
{% for idx, c in enumerate(config.allow_countries) %}
<li>{{ c }}
    <form action="{{ url_for('delete_allow_country', idx=idx) }}" method="post" style="display:inline">
        <button type="submit">Delete</button>
    </form>
</li>
{% endfor %}
</ul>
<form action="{{ url_for('add_allow_country') }}" method="post">
    Country Code: <input name="value" required>
    <button type="submit">Add</button>
</form>

<h2>Blocked Countries</h2>
<ul>
{% for idx, c in enumerate(config.block_countries) %}
<li>{{ c }}
    <form action="{{ url_for('delete_block_country', idx=idx) }}" method="post" style="display:inline">
        <button type="submit">Delete</button>
    </form>
</li>
{% endfor %}
</ul>
<form action="{{ url_for('add_block_country') }}" method="post">
    Country Code: <input name="value" required>
    <button type="submit">Add</button>
</form>
"""


@app.route("/")
def index():
    cfg = load_config(CONFIG_FILE)
    # Convert forward rules to objects with attribute access for Jinja2
    class Obj(dict):
        __getattr__ = dict.__getitem__
    cfg["forwards"] = [Obj(r) for r in cfg["forwards"]]
    return render_template_string(TEMPLATE, config=Obj(cfg))


def _mutate_list(key: str, value: str | None = None, idx: int | None = None) -> None:
    cfg = load_config(CONFIG_FILE)
    if value is not None:
        cfg[key].append(value)
    elif idx is not None and 0 <= idx < len(cfg[key]):
        cfg[key].pop(idx)
    save_config(CONFIG_FILE, cfg)
    apply_rules(cfg)


@app.route("/add_forward", methods=["POST"])
def add_forward():
    cfg = load_config(CONFIG_FILE)
    rule = {
        "local_port": int(request.form["local_port"]),
        "remote_ip": request.form["remote_ip"],
        "remote_port": int(request.form["remote_port"]),
    }
    cfg["forwards"].append(rule)
    save_config(CONFIG_FILE, cfg)
    apply_rules(cfg)
    return redirect(url_for("index"))


@app.route("/delete_forward/<int:idx>", methods=["POST"])
def delete_forward(idx: int):
    cfg = load_config(CONFIG_FILE)
    if 0 <= idx < len(cfg["forwards"]):
        cfg["forwards"].pop(idx)
        save_config(CONFIG_FILE, cfg)
        apply_rules(cfg)
    return redirect(url_for("index"))


@app.route("/add_allow_ip", methods=["POST"])
def add_allow_ip():
    _mutate_list("allow_ips", request.form["value"])
    return redirect(url_for("index"))


@app.route("/delete_allow_ip/<int:idx>", methods=["POST"])
def delete_allow_ip(idx: int):
    _mutate_list("allow_ips", idx=idx)
    return redirect(url_for("index"))


@app.route("/add_block_ip", methods=["POST"])
def add_block_ip():
    _mutate_list("block_ips", request.form["value"])
    return redirect(url_for("index"))


@app.route("/delete_block_ip/<int:idx>", methods=["POST"])
def delete_block_ip(idx: int):
    _mutate_list("block_ips", idx=idx)
    return redirect(url_for("index"))


@app.route("/add_allow_country", methods=["POST"])
def add_allow_country():
    _mutate_list("allow_countries", request.form["value"].upper())
    return redirect(url_for("index"))


@app.route("/delete_allow_country/<int:idx>", methods=["POST"])
def delete_allow_country(idx: int):
    _mutate_list("allow_countries", idx=idx)
    return redirect(url_for("index"))


@app.route("/add_block_country", methods=["POST"])
def add_block_country():
    _mutate_list("block_countries", request.form["value"].upper())
    return redirect(url_for("index"))


@app.route("/delete_block_country/<int:idx>", methods=["POST"])
def delete_block_country(idx: int):
    _mutate_list("block_countries", idx=idx)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
