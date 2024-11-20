from zabbix_api import ZabbixAPI

URL = "http://127.0.0.1"
USERNAME = "Admin"
PASSWORD = "zabbix"

try:
    zapi = ZabbixAPI(URL, timeout=150)
    zapi.login(USERNAME, PASSWORD)
    print(f'Conectado na API do Zabbix, versão {zapi.api_version()}')
except Exception as err:
    print(f'Falha ao conectar na API do Zabbix: {err}')

groupids = ['2', '7']
groups = [{"groupid": groupid} for groupid in groupids]

# Usando o template ID do "Template OS Linux"
templates = ['10001']
template = [{"templateid": templateid} for templateid in templates]

# Definindo as macros com sintaxe correta
macros = [
    {
        "macro": "{$USER_ID}",
        "value": "caio"
    },
    {
        "macro": "{$PASSWORD}",
        "value": "123"
    }
]


info_interfaces = {
    "1": {"type": "agent", "id": 1, "port": "10050"},
    "2": {"type": "SNMP", "id": 2, "port": "161"}
}

interface = {
    "type": info_interfaces['1']['id'],  # Usando a interface de agente
    "main": 1,
    "useip": 1,
    "ip": "192.168.105.251",
    "dns": "",
    "port": info_interfaces['1']['port']
}

print("Interface:", interface)

try:
    create_host = zapi.host.create({
        "groups": groups,
        "host": "teste-08967",
        "interfaces": [interface],
        "templates": template,
        "macros": macros
    })
    print('Host cadastrado com sucesso:', create_host)
except Exception as err:
    print(f'Falha ao cadastrar o host: {err}')
