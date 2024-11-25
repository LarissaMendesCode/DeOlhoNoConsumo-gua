from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = "chave-secreta"  # Necessário para o uso de sessões e mensagens flash

# Função para criar o banco de dados (executar apenas uma vez)
def criar_banco():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

#Página inicial (home)
@app.route("/")
def home():
    return render_template("Home.html")

# Página cálculo (index)
@app.route("/index", methods=["GET","POST"])
def index():
   return render_template("index.html")


@app.route('/resultado', methods=['GET', 'POST'])
def resultado():
    global calcular_desperdicio
    if request.method == 'POST':
        # Aqui entra a lógica de cálculo, adaptada conforme necessário
        desperdicio_total_m3 = calcular_desperdicio(request.form)
        
        # Renderiza o HTML com os resultados
        return render_template(
            "resultado.html",
            desperdicio_total_m3=desperdicio_total_m3
        )


# Rota para cadastro
@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)
        try:
            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO usuarios (username, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
            conn.close()
            flash("Cadastro realizado com sucesso!", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Usuário já existente!", "error")
    
    return render_template("Cadastro.html")


# Rota para login
@app.route("/Login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            session["user_id"] = user[0]
            flash("Login realizado com sucesso!", "success")
            return redirect(url_for("index"))
        else:
            flash("Credenciais inválidas!", "error")
    return render_template("Login.html")

# Rota para logout
@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("Logout realizado com sucesso!", "success")
    return redirect(url_for("Home"))


if __name__ == "__main__":
    criar_banco()  # Executa a criação do banco antes de rodar o servidor
    app.run(debug=True)

conn = sqlite3.connect("database.db", timeout=10)

