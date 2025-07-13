from modules.dump import dump_all_json
from modules.exporter import export_all_html_and_csv

if __name__ == "__main__":
    json_path = "save_json/"
    html_path = "save_html/"
    config_path = "config_secure.json"

    #dump_all_json(config_path=config_path, save_path=json_path)
    export_all_html_and_csv(json_path=json_path, html_path=html_path, use_color=True)
