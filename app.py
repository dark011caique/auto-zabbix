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
    ip = request.form['ip']
    template_id = request.form['template']
    macro_user = request.form.get('macro_user')
    macro_password = request.form.get('macro_password')

    try:
        zapi = ZabbixAPI(URL, timeout=150)
        zapi.login(USERNAME, PASSWORD)
        print(f'Conectado na API do Zabbix, versão {zapi.api_version()}')

        groupids = ['2', '7']
        groups = [{"groupid": groupid} for groupid in groupids]

        templates = [template_id]
        template = [{"templateid": templateid} for templateid in templates]

        # Definindo as macros opcionalmente
        macros = []
        if macro_user:
            macros.append({"macro": "{$USER_ID}", "value": macro_user})
        if macro_password:
            macros.append({"macro": "{$PASSWORD}", "value": macro_password})

        # Definição das interfaces
        info_interfaces = {
            "1": {"type": "agent", "id": 1, "port": "10050"},
            "2": {"type": "SNMP", "id": 2, "port": "161"}
        }

        interface = {
            "type": info_interfaces['1']['id'],  # Usando a interface de agente
            "main": 1,
            "useip": 1,
            "ip": ip,
            "dns": "",
            "port": info_interfaces['1']['port']
        }

        print("Interface:", interface)

        create_host = zapi.host.create({
            "groups": groups,
            "host": hostname,
            "interfaces": [interface],
            "templates": template,
            "macros": macros
        })

        return f'Host cadastrado com sucesso: {create_host}'
    except Exception as err:
        return f'Falha ao cadastrar o host: {err}'

if __name__ == '__main__':
    app.run(debug=True)
