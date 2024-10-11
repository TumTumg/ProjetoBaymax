import mysql.connector
from mysql.connector import Error


class Database:
    def __init__(self, host='localhost', user='root', password='', database='baymax'):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def create_connection(self):
        """Cria uma conexão com o banco de dados MySQL."""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                print(f"Conexão com o banco de dados '{self.database}' foi bem-sucedida.")
        except Error as e:
            print(f"Erro ao conectar ao MySQL: {e}")

    def close_connection(self):
        """Fecha a conexão com o banco de dados."""
        if self.connection.is_connected():
            self.connection.close()
            print("Conexão com o banco de dados fechada.")

    def create_user(self, username, senha):
        """Insere um novo usuário no banco de dados."""
        cursor = self.connection.cursor()
        comando = f'INSERT INTO usuario (id, username, senha) VALUES ("","{username}", "{senha}")'
        cursor.execute(comando)
        self.connection.commit()
        cursor.close()
        print(f"Usuário '{username}' criado com sucesso.")

    def read_users(self):
        """Lê todos os usuários do banco de dados."""
        cursor = self.connection.cursor()
        comando = 'SELECT * FROM usuário'
        cursor.execute(comando)
        resultado = cursor.fetchall()
        cursor.close()
        return resultado

    def update_user(self, username_antigo, username_novo, password_novo):
        """Atualiza um usuário existente no banco de dados."""
        cursor = self.connection.cursor()
        comando = f'UPDATE usuário SET username = "{username_novo}", password = "{password_novo}" WHERE username = "{username_antigo}"'
        cursor.execute(comando)
        self.connection.commit()
        cursor.close()
        print(f"Usuário '{username_antigo}' atualizado para '{username_novo}'.")

    def delete_user(self, username):
        """Deleta um usuário do banco de dados."""
        cursor = self.connection.cursor()
        comando = f'DELETE FROM usuário WHERE username = "{username}"'
        cursor.execute(comando)
        self.connection.commit()
        cursor.close()
        print(f"Usuário '{username}' deletado com sucesso.")


# Exemplo de uso
if __name__ == "__main__":
    db = Database()
    db.create_connection()

    # CREATE
    db.create_user("João", "senha123")

    # READ
    usuarios = db.read_users()
    print("Usuários no banco de dados:")
    for usuario in usuarios:
        print(usuario)

    # UPDATE
    db.update_user("João", "João Silva", "nova_senha123")

    # DELETE
    db.delete_user("João Silva")

    db.close_connection()
