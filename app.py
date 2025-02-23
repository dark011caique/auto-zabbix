from flask import Flask, request, render_template
from zabbix_api import ZabbixAPI

app = Flask(__name__)

URL = "http://127.0.0.1/api_jsonrpc.php"  # Ajustado o endpoint da API
USERNAME = "Admin"
PASSWORD = "zabbix"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_host', methods=['POST'])
def add_host():
    hostname = request.form['hostname']
    visible_name = request.form.get('visible_name', hostname)  # Se não for informado, usa hostname
    ip = request.form['ip']
    template_ids = request.form.getlist('template')  # Permite selecionar vários templates
    group_ids = request.form.getlist('group')  # Permite selecionar vários grupos
    macro_user = request.form.get('macro_user')
    macro_password = request.form.get('macro_password')
    description = request.form.get('description', '')  # Pode ser opcional
    proxy = request.form.get('proxy', '')  # Pode ser opcional
    interface_type = request.form.get('interface', '1')  # 1 = Agent (default), 2 = SNMP

    try:
        zapi = ZabbixAPI(URL, timeout=150)
        zapi.login(USERNAME, PASSWORD)
        print(f'Conectado na API do Zabbix, versão {zapi.api_version()}')

        # Definindo os grupos
        groups = [{"groupid": groupid} for groupid in group_ids]

        # Definindo os templates
        templates = [{"templateid": templateid} for templateid in template_ids]

        # Definição das macros opcionais
        macros = []
        if macro_user:
            macros.append({"macro": "{$USER_ID}", "value": macro_user})
        if macro_password:
            macros.append({"macro": "{$PASSWORD}", "value": macro_password})

        # Definição das interfaces
        info_interfaces = {
            "1": {"type": 1, "port": "10050"},  # Agent
            "2": {"type": 2, "port": "161"}  # SNMP
        }

        interface = {
            "type": info_interfaces[interface_type]["type"],
            "main": 1,
            "useip": 1,
            "ip": ip,
            "dns": "",
            "port": info_interfaces[interface_type]["port"]
        }

        print("Interface:", interface)

        # Criando o host no Zabbix
        create_host = zapi.host.create({
            "host": hostname,
            "name": visible_name,
            "groups": groups,
            "interfaces": [interface],
            "templates": templates,
            "macros": macros,
            "description": description,
            "proxy_hostid": proxy if proxy else None  # Adiciona proxy se definido
        })

        print("Host criado com sucesso:", create_host)
    except Exception as e:
        print("Erro ao criar host:", str(e))


if __name__ == '__main__':
    app.run(debug=True)
