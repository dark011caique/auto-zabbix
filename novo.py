from flask import Flask, request, render_template
from zabbix_api import ZabbixAPI
import paramiko

app = Flask(__name__)

# Configurações do Zabbix
URL = "http://127.0.0.1/api_jsonrpc.php"
USERNAME = "Admin"
PASSWORD = "zabbix"

# Configurações do servidor SSH
SSH_HOST = '192.168.0.108'
SSH_PORT = 22
SSH_USERNAME = 'caique'
SSH_PASSWORD = '123'  # Substitua pela senha correta

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_host', methods=['POST'])
def add_host():
    hostname = request.form['hostname']
    visible_name = request.form.get('visible_name', hostname)
    ip = request.form['ip']
    template_ids = request.form.getlist('template')
    group_ids = request.form.getlist('group')
    macro_user = request.form.get('macro_user')
    macro_password = request.form.get('macro_password')
    description = request.form.get('description', '')
    proxy = request.form.get('proxy', '')
    interface_type = request.form.get('interface', '1')

    # ODBC configuration parameters (only for template "banco de dados")
    odbc_description = request.form.get('odbc_description')
    odbc_server = request.form.get('odbc_server')
    odbc_database = request.form.get('odbc_database')
    odbc_user = request.form.get('odbc_user')
    odbc_password = request.form.get('odbc_password')
    odbc_port = request.form.get('odbc_port')

    try:
        zapi = ZabbixAPI(URL, timeout=150)
        zapi.login(USERNAME, PASSWORD)
        print(f'Conectado na API do Zabbix, versão {zapi.api_version()}')

        groups = [{"groupid": groupid} for groupid in group_ids]
        templates = [{"templateid": templateid} for templateid in template_ids]

        macros = []
        if macro_user:
            macros.append({"macro": "{$USER_ID}", "value": macro_user})
        if macro_password:
            macros.append({"macro": "{$PASSWORD}", "value": macro_password})

        info_interfaces = {
            "1": {"type": 1, "port": "10050"},
            "2": {"type": 2, "port": "161"}
        }

        interface = {
            "type": info_interfaces[interface_type]["type"],
            "main": 1,
            "useip": 1,
            "ip": ip,
            "dns": "",
            "port": info_interfaces[interface_type]["port"]
        }

        # Criar o host no Zabbix
        create_host = zapi.host.create({
            "host": hostname,
            "name": visible_name,
            "groups": groups,
            "interfaces": [interface],
            "templates": templates,
            "macros": macros,
            "description": description,
            "proxy_hostid": proxy if proxy else None
        })

        # Se o template de banco de dados foi selecionado, configurar ODBC
        if "101" in template_ids:  # template "banco de dados"
            configure_odbc(odbc_description, odbc_server, odbc_database, odbc_user, odbc_password, odbc_port)

        print("Host criado com sucesso:", create_host)
        return "Host cadastrado com sucesso!", 200
    except Exception as e:
        print("Erro ao criar host:", str(e))
        return str(e), 500

def configure_odbc(odbc_description, odbc_server, odbc_database, odbc_user, odbc_password, odbc_port):
    odbc_config = f"""
    [zabbix-odbc2]
    Description={odbc_description}
    Driver=MariaDB
    Server={odbc_server}
    Database={odbc_database}
    User={odbc_user}
    Password={odbc_password}
    Port={odbc_port}
    """

    # Configuração de SSH para atualizar o arquivo odbc.ini
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(SSH_HOST, SSH_PORT, SSH_USERNAME, SSH_PASSWORD)
        print("Conexão SSH estabelecida com sucesso!")

        temp_file = '/tmp/odbc_temp.ini'
        command = f"echo '{odbc_config}' > {temp_file}"
        client.exec_command(command)

        command = f"echo '{SSH_PASSWORD}' | sudo -S bash -c 'cat {temp_file} >> /etc/odbc.ini'"
        stdin, stdout, stderr = client.exec_command(command, get_pty=True)
        stdin.write(SSH_PASSWORD + "\n")
        stdin.flush()

        print(stdout.read().decode())
        print(stderr.read().decode())
        print("Monitoramento ODBC cadastrado com sucesso!")
    except Exception as e:
        print(f'Falha ao configurar o ODBC: {e}')
    finally:
        client.close()
        print("Conexão SSH encerrada.")

if __name__ == '__main__':
    app.run(debug=True)
