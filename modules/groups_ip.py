import os
import json
import pandas as pd
from modules.utils import css_style

def extract(objects):
    rows = []

    for obj in objects:
        if 'networkIpAddress' in obj:
            inet = obj['networkIpAddress'].get('inet', '')
            name = obj['networkIpAddress'].get('name', '')
            ip_type = obj['networkIpAddress'].get('type', '')
            rows.append(f"<tr><td><strong>{inet}</strong></td><td>{name}</td><td><i>{ip_type}</i></td></tr>")

        elif 'networkFqdn' in obj:
            fqdn = obj['networkFqdn'].get('fqdn', '')
            name = obj['networkFqdn'].get('name', '')
            fqdn_type = obj['networkFqdn'].get('type', '')
            rows.append(f"<tr><td><strong>{fqdn}</strong></td><td>{name}</td><td><i>{fqdn_type}</i></td></tr>")

        elif 'networkGroup' in obj:
            name = obj['networkGroup'].get('name', '')
            desc = obj['networkGroup'].get('description', '')
            group_type = 'networkGroup'
            rows.append(f"<tr><td><strong>{name}</strong></td><td>{desc}</td><td><i>{group_type}</i></td></tr>")

        elif 'networkGeoAddress' in obj:
            desc = obj['networkGeoAddress'].get('description', '')
            name = obj['networkGeoAddress'].get('name', '')
            geo_type = obj['networkGeoAddress'].get('type', '')
            rows.append(f"<tr><td><strong>{desc}</strong></td><td>{name}</td><td><i>{geo_type}</i></td></tr>")

        elif 'networkIpRange' in obj:
            from_range = obj['networkIpRange'].get('from', '')
            to_range = obj['networkIpRange'].get('to', '')
            name = obj['networkIpRange'].get('name', '')
            range_type = obj['networkIpRange'].get('type', '')
            rows.append(f"<tr><td><strong>{from_range} - {to_range}</strong></td><td>{name}</td><td><i>{range_type}</i></td></tr>")

    return f'<table border="1" cellpadding="4" style="border-collapse: collapse; width: 100%;"><tbody>{"".join(rows)}</tbody></table>'


def export_ip_groups(json_path, html_path):
    with open(os.path.join(json_path, "env.json")) as f:
        env = json.load(f)

    with open(os.path.join(json_path, "groups_ip.json")) as f:
        data = json.load(f)

    records = []
    for item in data:
        records.append({
            "Name": item["group"].get("name", ""),
            "Description": item["group"].get("description", ""),
            "Value | Name | Type": extract(item["group"].get("items", {}))
        })

    df = pd.DataFrame(records)

    html_header = f'''
    <div class="container">
        <h3>Groups IP</h3>
        <p>IP адрес системы управления: <strong>{env.get("mgmt_ip")}</strong></p>
        <p>Имя группы: <strong>{env.get("groupe_name")}</strong></p>
        <p>Приоритет: <strong>{env.get("precedence")}</strong></p>
    '''

    html = css_style + html_header + df.to_html(classes='dataframe', escape=False, index=False) + "</div>"

    output_file = os.path.join(html_path, f"{env['groupe_name']}_groups_ip.html")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[+] IP-группы экспортированы в {output_file}")
