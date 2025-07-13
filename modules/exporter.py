import os
from modules.rules import export_rules
from modules.groups_ip import export_ip_groups
from modules.groups_service import export_service_groups
from modules.where_ip import export_where_ip
from modules.objects_csv import export_objects_to_csv


def export_all_html_and_csv(json_path, html_path, use_color=True, csv_path=None):
    os.makedirs(html_path, exist_ok=True)
    if csv_path:
        os.makedirs(csv_path, exist_ok=True)
    else:
        csv_path = html_path

    export_rules(json_path, html_path, use_color, csv_path)
    export_ip_groups(json_path, html_path)
    export_service_groups(json_path, html_path)
    export_where_ip(json_path, html_path)
    export_objects_to_csv(json_path, csv_path)
