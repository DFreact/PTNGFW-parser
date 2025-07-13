import os
import json
import pandas as pd
from modules.utils import css_style

def extract(objects):
    rows = []

    for obj in objects:
        if 'service' in obj:
            name = obj['service'].get('name', '')
            proto = obj['service'].get('protocol', '').replace("SERVICE_PROTOCOL_", "")
            src = dst = ""

            src_ports = obj['service'].get('srcPorts', [])
            if src_ports:
                if 'singlePort' in src_ports[0]:
                    src = "<br>".join(str(p['singlePort']['port']) for p in src_ports)
                elif 'portRange' in src_ports[0]:
                    src = "<br>".join(f"{p['portRange']['from']}-{p['portRange']['to']}" for p in src_ports)

            dst_ports = obj['service'].get('dstPorts', [])
            if dst_ports:
                if 'singlePort' in dst_ports[0]:
                    dst = "<br>".join(str(p['singlePort']['port']) for p in dst_ports)
                elif 'portRange' in dst_ports[0]:
                    dst = "<br>".join(f"{p['portRange']['from']}-{p['portRange']['to']}" for p in dst_ports)

            rows.append(f"<tr><td><strong>{src}</strong></td><td><strong>{dst}</strong></td><td>{name}</td><td><i>{proto}</i></td></tr>")

        elif 'serviceGroup' in obj:
            name = obj['serviceGroup'].get('name', '')
            rows.append(f"<tr><td></td><td></td><td>{name}</td><td><i>Group</i></td></tr>")

    return f'<table border="1" cellpadding="4" style="border-collapse: collapse; width: 100%;"><tbody>{"".join(rows)}</tbody></table>'


def export_service_groups(json_path, html_path):
    with open(os.path.join(json_path, "env.json")) as f:
        env = json.load(f)

    with open(os.path.join(json_path, "groups_service.json")) as f:
        data = json.load(f)

    records = []
    for item in data:
        records.append({
            "Name": item["serviceGroup"].get("name", ""),
            "Description": item["serviceGroup"].get("description", ""),
            "SRC | DST | Name | Type": extract(item["serviceGroup"].get("items", {}))
        })

    df = pd.DataFrame(records)

    html_header = f'''
    <div class="container">
        <h3>Service Groups</h3>
        <p>IP адрес системы управления: <strong>{env.get("mgmt_ip")}</strong></p>
        <p>Имя группы: <strong>{env.get("groupe_name")}</strong></p>
        <p>Приоритет: <strong>{env.get("precedence")}</strong></p>
    '''

    html = css_style + html_header + df.to_html(classes='dataframe', escape=False, index=False) + "</div>"

    output_file = os.path.join(html_path, f"{env['groupe_name']}_groups_service.html")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[+] Сервис-группы экспортированы в {output_file}")
