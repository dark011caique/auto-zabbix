from zabbix_api import ZabbixAPI
import paramiko

# Dados de conexão com o Zabbix
URL = "http://127.0.0.1"
USERNAME = "Admin"
PASSWORD = "zabbix"

# Configurações do servidor SSH
hostname = '192.168.0.108'
port = 22
ssh_username = 'caique'
ssh_password = '123'  # Coloque a senha correta para SSH

# Função para configurar o ODBC via SSH
def configure_odbc():
    # Cria um cliente SSH
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Conecta ao servidor via SSH
        client.connect(hostname, port, ssh_username, ssh_password)
        print("Conexão SSH estabelecida com sucesso!")

        # Comando para criar o arquivo temporário com a configuração do ODBC
        odbc_config = """
[zabbix-odbc2]
Description=Zabbix ODBC MySQL Connection 2
Driver=MariaDB
Server=127.0.0.1
Database=zabbix_proxy2
User=zabbix
Password=1234
Port=3306"""

        temp_file = '/tmp/odbc_temp.ini'

        # Comando para criar o arquivo temporário
        command = f"echo '{odbc_config}' > {temp_file}"
        stdin, stdout, stderr = client.exec_command(command)
        print(stdout.read().decode())
        print(stderr.read().decode())

        # Comando para adicionar o conteúdo do arquivo temporário ao odbc.ini com sudo
        command = f"echo '{ssh_password}' | sudo -S bash -c 'cat {temp_file} >> /etc/odbc.ini'"
        stdin, stdout, stderr = client.exec_command(command, get_pty=True)
        stdin.write(ssh_password + "\n")
        stdin.flush()

        print(stdout.read().decode())
        print(stderr.read().decode())

        print("Monitoramento ODBC cadastrado com sucesso!")

    except Exception as e:
        print(f'Falha ao configurar o ODBC: {e}')
    finally:
        # Fecha a conexão SSH
        client.close()
        print("Conexão SSH encerrada.")

# Função para conectar na API do Zabbix e criar o host
def create_zabbix_host():
    try:
        zapi = ZabbixAPI(URL, timeout=150)
        zapi.login(USERNAME, PASSWORD)
        print(f'Conectado na API do Zabbix, versão {zapi.api_version()}')

        # Grupos, templates e macros
        groupids = ['2', '7']
        groups = [{"groupid": groupid} for groupid in groupids]

        templates = ['10001']
        template = [{"templateid": templateid} for templateid in templates]

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

        # Criação do host no Zabbix
        create_host = zapi.host.create({
            "groups": groups,
            "host": "adiq",
            "interfaces": [interface],
            "templates": template,
            "macros": macros
        })

        print('Host cadastrado com sucesso:', create_host)

    except Exception as err:
        print(f'Falha ao conectar na API do Zabbix ou cadastrar o host: {err}')

# Passo 2: Criar o host no Zabbix
create_zabbix_host()

# Passo 1: Configurar o ODBC via SSH
configure_odbc()
