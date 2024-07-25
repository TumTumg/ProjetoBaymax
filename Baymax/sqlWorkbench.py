import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error

class SQLWorkbench:
    def __init__(self, root):
        self.root = root
        self.root.title("SQL Workbench")
        self.root.geometry("800x600")

        # Conexão ao banco de dados
        self.conn = None
        self.cursor = None

        # Interface
        self.setup_gui()

    def setup_gui(self):
        # Entrada para o nome do host
        self.host_label = tk.Label(self.root, text="Host do Banco de Dados:")
        self.host_label.pack(pady=5)
        self.host_entry = tk.Entry(self.root, width=50)
        self.host_entry.pack(pady=5)

        # Entrada para o nome do banco de dados
        self.db_label = tk.Label(self.root, text="Nome do Banco de Dados:")
        self.db_label.pack(pady=5)
        self.db_entry = tk.Entry(self.root, width=50)
        self.db_entry.pack(pady=5)

        # Entrada para o nome de usuário
        self.user_label = tk.Label(self.root, text="Usuário:")
        self.user_label.pack(pady=5)
        self.user_entry = tk.Entry(self.root, width=50)
        self.user_entry.pack(pady=5)

        # Entrada para a senha
        self.password_label = tk.Label(self.root, text="Senha:")
        self.password_label.pack(pady=5)
        self.password_entry = tk.Entry(self.root, show="*", width=50)
        self.password_entry.pack(pady=5)

        # Botão para conectar ao banco de dados
        self.connect_button = tk.Button(self.root, text="Conectar", command=self.connect_db)
        self.connect_button.pack(pady=5)

        # Área de texto para entrada SQL
        self.sql_text = tk.Text(self.root, height=10)
        self.sql_text.pack(pady=5)

        # Botão para executar a consulta
        self.run_button = tk.Button(self.root, text="Executar", command=self.run_query)
        self.run_button.pack(pady=5)

        # Tabela para mostrar os resultados
        self.results_tree = ttk.Treeview(self.root)
        self.results_tree.pack(pady=5, fill=tk.BOTH, expand=True)

    def connect_db(self):
        host = self.host_entry.get()
        db_name = self.db_entry.get()
        user = self.user_entry.get()
        password = self.password_entry.get()

        try:
            self.conn = mysql.connector.connect(
                host=host,
                database=db_name,
                user=user,
                password=password
            )
            if self.conn.is_connected():
                self.cursor = self.conn.cursor()
                messagebox.showinfo("Conexão", f"Conectado ao banco de dados {db_name}")
        except Error as e:
            messagebox.showerror("Erro", f"Erro ao conectar ao banco de dados: {e}")

    def run_query(self):
        query = self.sql_text.get("1.0", tk.END).strip()
        if not query:
            messagebox.showwarning("Aviso", "Digite uma consulta SQL.")
            return

        try:
            self.cursor.execute(query)
            if query.lower().startswith("select"):
                rows = self.cursor.fetchall()
                self.show_results(rows)
            else:
                self.conn.commit()
                messagebox.showinfo("Sucesso", "Consulta executada com sucesso.")
        except Error as e:
            messagebox.showerror("Erro", f"Erro ao executar a consulta: {e}")

    def show_results(self, rows):
        for row in self.results_tree.get_children():
            self.results_tree.delete(row)

        columns = [description[0] for description in self.cursor.description]
        self.results_tree["columns"] = columns
        self.results_tree["show"] = "headings"

        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=100)

        for row in rows:
            self.results_tree.insert("", tk.END, values=row)

if __name__ == "__main__":
    root = tk.Tk()
    app = SQLWorkbench(root)
    root.mainloop()
