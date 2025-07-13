import os
import json
import csv


def export_objects_to_csv(json_path, html_path):
    with open(os.path.join(json_path, "ip.json"), "r", encoding="utf-8") as f:
        ip_data = json.load(f)

    with open(os.path.join(json_path, "groups_ip.json"), "r", encoding="utf-8") as f:
        group_data = json.load(f)

    # Индексация по ID
    id_to_groups = {}
    for group in group_data:
        group_name = group.get("group", {}).get("name", "")
        for item in group.get("group", {}).get("items", []):
            for key in ["networkIpAddress", "networkIpRange"]:
                obj = item.get(key)
                if obj and "id" in obj:
                    id_to_groups.setdefault(obj["id"], []).append(group_name)

    objects = []

    for item in ip_data.get("addresses", []):
        obj_id = item.get("id")
        objects.append({
            "id": obj_id,
            "name": item.get("name", ""),
            "ip": item.get("inet", ""),
            "group": ", ".join(id_to_groups.get(obj_id, []))
        })

    for item in ip_data.get("ranges", []):
        obj_id = item.get("id")
        ip_range = f"{item.get('from', '')} - {item.get('to', '')}"
        objects.append({
            "id": obj_id,
            "name": item.get("name", ""),
            "ip": ip_range,
            "group": ", ".join(id_to_groups.get(obj_id, []))
        })

    output_file = os.path.join(html_path, "ip_group.csv")
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "name", "ip", "group"], delimiter="|")
        writer.writeheader()
        writer.writerows(objects)

    print(f"[+] CSV ip_group экспортирован в {output_file}")
