import os
import json
import pandas as pd
from modules.utils import css_style


def extract_names(objects):
    result = []
    if isinstance(objects, dict):
        for key, value in objects.items():
            if key == "name":
                result.append(value)
            else:
                result.extend(extract_names(value))
    elif isinstance(objects, list):
        for item in objects:
            result.extend(extract_names(item))
    return result


def check_ip_match(ip_obj, ip_name):
    for k in ["networkIpAddress", "networkGroup", "networkFqdn", "networkIpRange"]:
        if k in ip_obj and ip_name == ip_obj[k].get("name", ""):
            return True
    return False


def extract_name_rules(ip_name, rules_data):
    src_rows, dst_rows = [], []

    for rule in rules_data.get("items", []):
        for src in rule.get("sourceAddr", {}).get("objects", []):
            if check_ip_match(src, ip_name):
                src_rows.append(rule.get("name", ""))
        for dst in rule.get("destinationAddr", {}).get("objects", []):
            if check_ip_match(dst, ip_name):
                dst_rows.append(rule.get("name", ""))

    max_len = max(len(src_rows), len(dst_rows))
    src_rows += [""] * (max_len - len(src_rows))
    dst_rows += [""] * (max_len - len(dst_rows))

    rows_html = "".join(f"<tr><td>{s}</td><td>{d}</td></tr>" for s, d in zip(src_rows, dst_rows))

    return f"<table border='1'><thead><tr><th>Source</th><th>Destination</th></tr></thead><tbody>{rows_html}</tbody></table>"


def extract_name_nat(ip_name, nat_data):
    src, dst, src_tr, dst_tr = [], [], [], []

    for rule in nat_data.get("items", []):
        if any(check_ip_match(i, ip_name) for i in rule.get("sourceAddr", {}).get("objects", [])):
            src.append(rule.get("name", ""))
        if any(check_ip_match(i, ip_name) for i in rule.get("destinationAddr", {}).get("objects", [])):
            dst.append(rule.get("name", ""))
        if any(check_ip_match(i, ip_name) for i in rule.get("srcTranslatedAddress", {}).get("objects", [])):
            src_tr.append(rule.get("name", ""))
        if any(check_ip_match(i, ip_name) for i in rule.get("dstTranslatedAddress", {}).get("objects", [])):
            dst_tr.append(rule.get("name", ""))

    max_len = max(len(src), len(dst), len(src_tr), len(dst_tr))
    src += [""] * (max_len - len(src))
    dst += [""] * (max_len - len(dst))
    src_tr += [""] * (max_len - len(src_tr))
    dst_tr += [""] * (max_len - len(dst_tr))

    rows_html = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td><td>{d}</td></tr>" for a, b, c, d in zip(src, dst, src_tr, dst_tr))

    return f"<table border='1'><thead><tr><th>Source</th><th>Destination</th><th>Src Translated</th><th>Dst Translated</th></tr></thead><tbody>{rows_html}</tbody></table>"


def extract_name_group_ip(ip_name, groups_data):
    names = []
    for group in groups_data:
        for item in group.get("group", {}).get("items", []):
            if check_ip_match(item, ip_name):
                names.append(group["group"].get("name", ""))

    rows = "".join(f"<tr><td>{name}</td></tr>" for name in names)
    return f"<table border='1'><thead><tr><th>Group Name</th></tr></thead><tbody>{rows}</tbody></table>"


def export_where_ip(json_path, html_path):
    with open(os.path.join(json_path, "env.json")) as f:
        env = json.load(f)

    ip_data = json.load(open(os.path.join(json_path, "ip.json")))
    rules_data = json.load(open(os.path.join(json_path, "rules.json")))
    nat_data = json.load(open(os.path.join(json_path, "nat.json")))
    groups_data = json.load(open(os.path.join(json_path, "groups_ip.json")))

    ip_names = extract_names(ip_data)
    records = []

    for ip_name in ip_names:
        records.append({
            "name Address": ip_name,
            "name security rules": extract_name_rules(ip_name, rules_data),
            "name nat rules": extract_name_nat(ip_name, nat_data),
            "name address group": extract_name_group_ip(ip_name, groups_data)
        })

    df = pd.DataFrame(records)

    html_header = f'''
    <div class="container">
        <h3>Where IP</h3>
        <p>IP адрес системы управления: <strong>{env.get("mgmt_ip")}</strong></p>
        <p>Имя группы: <strong>{env.get("groupe_name")}</strong></p>
        <p>Приоритет: <strong>{env.get("precedence")}</strong></p>
    </div>
    '''

    html = css_style + html_header + df.to_html(classes="dataframe", escape=False, index=False) + "</div>"

    output_file = os.path.join(html_path, f"{env['groupe_name']}_where_IP.html")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[+] Where-IP отчёт экспортирован в {output_file}")
