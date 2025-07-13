import json
import os

color_ip = "#507EA4"
color_net_gr = "#EB7852"
color_geo = "#7FB99D"
color_fqdn = "#DF8743"
color_net_range = "#ED7AA1"
color_tcp = "#42516F"
color_udp = "#FF6347"
color_service_gr = "#48BFAD"

group_cache = {}

css_style = """
<style type="text/css">
.container {
    width: 80%;
    margin: auto;
    text-align: center;
}
th { text-align: center; }
.dataframe tbody td { white-space: nowrap; }
.dataframe {
    margin: auto;
    border-collapse: separate;
}
.dataframe thead th {
    background-color: #f2f2f2;
    color: #333;
}
.dataframe tbody tr:nth-child(even) {
    background-color: #f9f9f9;
}
.dataframe tbody tr:hover {
    background-color: #f1f1f1;
}
.dataframe th, .dataframe td {
    padding: 5px;
    text-align: left;
}
.dataframe td:nth-child(4),
.dataframe th:nth-child(4) {
    max-width: 150px;
    word-wrap: break-word;
    white-space: normal;
}
.dataframe td:nth-child(15),
.dataframe th:nth-child(15) {
    max-width: 200px;
    word-wrap: break-word;
    white-space: normal;
}
</style>
"""

legend_html = f"""
<div style="margin-top: 12px; font-weight: bold; text-align: center;">
    <table border="1" cellspacing="0" cellpadding="5" style="font-size: 18px; border-collapse: collapse; width: auto; table-layout: fixed; margin: 0 auto;">
        <tr><th>Название</th><th>Цвет</th></tr>
        <tr><td>network Ip Address</td><td style="background-color: {color_ip}; color: white;"></td></tr>
        <tr><td>network Group</td><td style="background-color: {color_net_gr}; color: white;"></td></tr>
        <tr><td>network Geo Address</td><td style="background-color: {color_geo}; color: white;"></td></tr>
        <tr><td>network Fqdn</td><td style="background-color: {color_fqdn}; color: white;"></td></tr>
        <tr><td>network Range</td><td style="background-color: {color_net_range}; color: white;"></td></tr>
        <tr><td>service TCP</td><td style="background-color: {color_tcp}; color: white;"></td></tr>
        <tr><td>service UDP</td><td style="background-color: {color_udp}; color: white;"></td></tr>
        <tr><td>service Group</td><td style="background-color: {color_service_gr}; color: white;"></td></tr>
    </table>
</div>
"""

def extract_name(objects, key):
    return "<br>".join([obj.get(key, "") for obj in objects])


def extract_name_or_ip(objects, use_color, json_path):
    global group_cache
    if "groups_ip" not in group_cache:
        with open(os.path.join(json_path, "groups_ip.json"), "r", encoding="utf-8") as f:
            group_cache["groups_ip"] = json.load(f)

    ip_list = []

    for obj in objects:
        if "networkIpAddress" in obj:
            val = obj["networkIpAddress"].get("inet", "")
            ip_list.append(colorize(val, color_ip, use_color))
        elif "networkGroup" in obj:
            name = obj["networkGroup"].get("name", "")
            group_ips = extract_ip_from_group(name, group_cache["groups_ip"])
            for ip in group_ips:
                ip_list.append(colorize(ip, color_net_gr, use_color))
        elif "networkGeoAddress" in obj:
            val = obj["networkGeoAddress"].get("name", "")
            ip_list.append(colorize(val, color_geo, use_color))
        elif "networkFqdn" in obj:
            val = obj["networkFqdn"].get("fqdn", "")
            ip_list.append(colorize(val, color_fqdn, use_color))
        elif "networkIpRange" in obj:
            ip_from = obj["networkIpRange"].get("from", "")
            ip_to = obj["networkIpRange"].get("to", "")
            val = f"{ip_from} - {ip_to}"
            ip_list.append(colorize(val, color_net_range, use_color))
        else:
            ip_list.append("Error")

    return "<br>".join(ip_list)


def extract_name_or_port(service_obj, use_color):
    ports = []
    for obj in service_obj.get("objects", []):
        if "service" in obj:
            proto = obj["service"].get("protocol", "")
            name = obj["service"].get("name", "")
            if proto == "SERVICE_PROTOCOL_TCP":
                ports.append(colorize(name, color_tcp, use_color))
            elif proto == "SERVICE_PROTOCOL_UDP":
                ports.append(colorize(name, color_udp, use_color))
            else:
                ports.append(name)
        elif "serviceGroup" in obj:
            name = obj["serviceGroup"].get("name", "")
            ports.append(colorize(name, color_service_gr, use_color))
        else:
            ports.append("Error")
    return "<br>".join(ports)


def extract_ip_from_group(name, group_data):
    for group in group_data:
        g = group.get("group", {})
        if g.get("name") == name:
            return [
                item.get("networkIpAddress", {}).get("inet")
                for item in g.get("items", [])
                if "networkIpAddress" in item
            ]
    return ["No group"]


def colorize(text, color, active):
    return f'<span style="color: {color}">{text}</span>' if active else text

import re

def strip_html(value):
    if isinstance(value, str):
        return re.sub(r'<[^>]*>', '', value)
    return value
