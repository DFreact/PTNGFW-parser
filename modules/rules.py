import os
import json
import pandas as pd
from modules.utils import (
    extract_name,
    extract_name_or_ip,
    extract_name_or_port,
    css_style,
    legend_html,
    strip_html
)

def export_rules(json_path, html_path, use_color=True, csv_path=None):
    with open(os.path.join(json_path, "env.json"), "r", encoding="utf-8") as f:
        env = json.load(f)

    with open(os.path.join(json_path, "rules.json"), "r", encoding="utf-8") as f:
        data = json.load(f)

    mgmt_ip = env.get("mgmt_ip")
    groupe_name = env.get("groupe_name")
    precedence = env.get("precedence")

    html_header = f'''
    <div class="container">
        <h3>Security Rules</h3>
        <p>IP адрес системы управления: <strong>{mgmt_ip}</strong></p>
        <p>Имя группы: <strong>{groupe_name}</strong></p>
        <p>Приоритет: <strong>{precedence}</strong></p>
    </div>
    '''

    records_html = []
    records_csv = []

    for item in data["items"]:
        base_fields = {
            "Enabled": item.get("enabled", ""),
            "Name": item.get("name", ""),
            "Description": item.get("description", ""),
            "Source Zone": extract_name(item.get("sourceZone", {}).get("objects", []), "name"),
            "Destination Zone": extract_name(item.get("destinationZone", {}).get("objects", []), "name"),
            "Application": extract_name(item.get("application", {}).get("objects", []), "name"),
            "URL Category": extract_name(item.get("urlCategory", {}).get("objects", []), "name"),
            "IPS": item.get("ipsProfile", {}).get("name", ""),
            "Antivirus": item.get("avProfile", {}).get("name", ""),
            "Log Mode": item.get("logMode", "").replace("SECURITY_RULE_LOG_MODE_", ""),
            "Schedule": item.get("schedule", "")
        }

        records_html.append({
            **base_fields,
            "Source IP": extract_name_or_ip(item.get("sourceAddr", {}).get("objects", []), use_color=True, json_path=json_path),
            "Destination IP": extract_name_or_ip(item.get("destinationAddr", {}).get("objects", []), use_color=True, json_path=json_path),
            "Service": extract_name_or_port(item.get("service", {}), use_color=True),
        })

        records_csv.append({
            **base_fields,
            "Source IP": extract_name_or_ip(item.get("sourceAddr", {}).get("objects", []), use_color=False, json_path=json_path),
            "Destination IP": extract_name_or_ip(item.get("destinationAddr", {}).get("objects", []), use_color=False, json_path=json_path),
            "Service": extract_name_or_port(item.get("service", {}), use_color=False),
        })

    df_html = pd.DataFrame(records_html)
    df_csv = pd.DataFrame(records_csv)

    html = css_style + html_header + df_html.to_html(classes='dataframe', escape=False, index=False)
    if use_color:
        html += legend_html
    html += "</div>"

    suffix = "_rules_color.html" if use_color else "_rules.html"
    with open(os.path.join(html_path, f"{groupe_name}{suffix}"), "w", encoding="utf-8") as f:
        f.write(html)

    csv_path = csv_path or html_path
    csv_file = os.path.join(csv_path, "pt-Rules-to-Csv.csv")
    df_csv.to_csv(csv_file, sep="|", index=False)

    print("[+] Правила экспортированы: HTML + CSV")
