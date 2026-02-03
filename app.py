import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)

@app.route('/')
def home():
   return render_template('home.html')


def get_db_connection():
  conn = sqlite3.connect('estoque.db')
  conn.row_factory = sqlite3.Row
  return conn

@app.route('/adicionar_produto')
def adicionar_produto():
  return render_template('adicionar_produto.html')

email_correto = "gabrielverri0108@gmail.com"
senha_correta = "gvpn0108"
@app.route('/login', methods=['GET','POST'])
def login():
    mensagem = ''

    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        if email == email_correto and senha == senha_correta:
            # mensagem = 'Login bem-sucedido'
            return redirect(url_for('adicionar_produto'))
        else:
            mensagem = 'Login ou senha incorretos'

    return render_template('login.html', mensagem = mensagem)


@app.route("/salvar_produto", methods=["POST"])
def salvar_produto():
    nome = request.form["nome"]
    codigo = request.form["codigo"]
    categoria = request.form["categoria"]
    quantidade = int(request.form["quantidade"])
    estoque_minimo = int(request.form["estoque_minimo"])
    preco_custo = request.form["preco_custo"]
    preco_venda = request.form["preco_venda"]

    conn = get_db_connection()
    cursor = conn.cursor()

    # cadastra o produto
    cursor.execute("""
        INSERT INTO produtos 
        (nome, codigo, categoria, quantidade, estoque_minimo, preco_custo, preco_venda)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (nome, codigo, categoria, quantidade, estoque_minimo, preco_custo, preco_venda))

    produto_id = cursor.lastrowid

    # registra a movimentação inicial (entrada)
    cursor.execute("""
        INSERT INTO movimentacoes (produto_id, tipo, quantidade, usuario_id)
        VALUES (?, 'entrada', ?, 1)
    """, (produto_id, quantidade))

    conn.commit()
    conn.close()

    return redirect(url_for("adicionar_produto"))

@app.route("/estoque")
def estoque():
    conn = sqlite3.connect("estoque.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM produtos")
    produtos = cursor.fetchall()

    conn.close()
    return render_template("estoque.html", produtos=produtos)



if __name__ == "__main__":
    app.run(debug=True)