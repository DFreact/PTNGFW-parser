import json, os
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

cookies = ""
headers = {"Content-Type": "application/json"}
global_group_id = ""


def dump_all_json(config_path, save_path):
    global cookies, global_group_id

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    mgmt_ip = config["mgmt_ip"]
    mgmt_login = config["mgmt_login"]
    mgmt_pass = config["mgmt_pass"]
    groupe_name = config["groupe_name"]
    precedence = config["precedence"]

    def request(endpoint, payload=None):
        url = f"https://{mgmt_ip}/api/v2/{endpoint}"
        resp = requests.post(url, headers=headers, json=payload, verify=False, cookies=cookies)
        resp.raise_for_status()
        return resp.json()

    # Авторизация
    resp = requests.post(
        f"https://{mgmt_ip}/api/v2/Login",
        json={"login": mgmt_login, "password": mgmt_pass},
        headers=headers,
        verify=False,
    )
    if resp.status_code != 200:
        raise Exception("Auth failed")
    cookies = resp.cookies

    def find_group_id(groups):
        if groups.get("name") == groupe_name:
            return groups["id"]
        for subgroup in groups.get("subgroups", []):
            result = find_group_id(subgroup)
            if result:
                return result
        return None

    # Получить ID группы
    tree = request("GetDeviceGroupsTree")
    global_group_id = find_group_id(tree["groups"][0])

    if not global_group_id:
        raise Exception("Group not found")

    # Сохраняем конфиг
    with open(os.path.join(save_path, "env.json"), "w") as f:
        json.dump({
            "mgmt_ip": mgmt_ip,
            "groupe_name": groupe_name,
            "precedence": precedence
        }, f)

    def save_data(endpoint, file_name, payload=None):
        data = request(endpoint, payload)
        with open(os.path.join(save_path, file_name), "w") as f:
            json.dump(data, f)

    def save_group_objects(endpoint_list, endpoint_get, key, file_name):
        ids = request(endpoint_list, {"limit": 10000, "deviceGroupId": global_group_id})[key]
        group_data = []
        for item in ids:
            res = requests.post(
                f"https://{mgmt_ip}/api/v2/{endpoint_get}",
                json={"id": item["id"]},
                headers=headers,
                cookies=cookies,
                verify=False
            )
            if res.status_code == 200:
                group_data.append(res.json())
        with open(os.path.join(save_path, file_name), "w") as f:
            json.dump(group_data, f)

    save_data("ListSecurityRules", "rules.json", {
        "limit": 10000, "deviceGroupId": global_group_id, "precedence": precedence
    })
    save_data("ListNatRules", "nat.json", {
        "limit": 10000, "deviceGroupId": global_group_id, "precedence": precedence
    })
    save_data("ListNetworkObjects", "ip.json", {
        "limit": 10000, "deviceGroupId": global_group_id,
        "precedence": precedence,
        "objectKinds": ["OBJECT_NETWORK_KIND_IPV4_ADDRESS", "OBJECT_NETWORK_KIND_IPV4_RANGE", "OBJECT_NETWORK_KIND_FQDN"]
    })
    save_group_objects("ListNetworkObjectGroups", "GetNetworkObjectGroup", "groups", "groups_ip.json")
    save_group_objects("ListServiceGroups", "GetServiceGroup", "serviceGroups", "groups_service.json")
