import configparser
import os

def add_dsn_to_odbc(driver, server, user, password, port, database, dsn_name, file_path='odbc.ini'):
    config = configparser.ConfigParser()

    # Verifica se o arquivo odbc.ini existe
    if not os.path.isfile(file_path):
        with open(file_path, 'w') as f:
            f.write("")

    try:
        config.read(file_path)
    except configparser.ParsingError as e:
        print(f"Erro de parsing ao ler {file_path}: {e}")
        return

    # Adiciona a nova seção DSN
    config[dsn_name] = {
        'Driver': driver,
        'Server': server,
        'User': user,
        'Password': password,
        'Port': port,
        'Database': database
    }

    # Salva as alterações no arquivo odbc.ini
    with open(file_path, 'w') as configfile:
        config.write(configfile)
    print(f"DSN '{dsn_name}' adicionado com sucesso ao {file_path}.")

if __name__ == "__main__":
    # Informações do banco de dados
    driver = input("Driver (por exemplo, MySQL): ")
    server = input("Servidor (por exemplo, localhost): ")
    user = input("Usuário: ")
    password = input("Senha: ")
    port = input("Porta (por exemplo, 3306): ")
    database = input("Nome do banco de dados: ")
    dsn_name = input("Nome do DSN: ")

    # Adiciona o DSN ao odbc.ini
    add_dsn_to_odbc(driver, server, user, password, port, database, dsn_name)
