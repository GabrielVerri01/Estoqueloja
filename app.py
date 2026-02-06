import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
# chave necessária para usar `flash()` e sessão
app.secret_key = "dev_secret_key_change_me"

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

    # selecionar colunas explicitamente para manter a ordem usada nos templates
    cursor.execute("SELECT id, nome, quantidade, estoque_minimo FROM produtos")
    produtos = cursor.fetchall()

    conn.close()
    return render_template("estoque.html", produtos=produtos)

@app.route("/pedir_prod")
def pedir_prod():
    conn = sqlite3.connect("estoque.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, nome, quantidade, estoque_minimo FROM produtos WHERE quantidade <= estoque_minimo")
    produtos = cursor.fetchall()

    conn.close()
    return render_template("pedir_prod.html", produtos=produtos)


@app.route("/att_semanal")
def att_semanal():
    return render_template("att_semanal.html")


@app.route("/salvar_att_semanal", methods=["POST"])
def salvar_att_semanal():
    nome = request.form.get("nome", "").strip()
    codigo = request.form.get("codigo", "").strip()
    try:
        new_q = int(request.form.get("quantidade", 0))
    except ValueError:
        flash("Quantidade inválida")
        return redirect(url_for("att_semanal"))

    conn = get_db_connection()
    cursor = conn.cursor()

    produto = None
    if codigo:
        cursor.execute("SELECT id, nome, quantidade, estoque_minimo FROM produtos WHERE codigo = ?", (codigo,))
        produto = cursor.fetchone()

    if produto is None and nome:
        cursor.execute("SELECT id, nome, quantidade, estoque_minimo FROM produtos WHERE nome = ?", (nome,))
        produto = cursor.fetchone()

    if produto is None:
        conn.close()
        flash("Produto não encontrado")
        return redirect(url_for("att_semanal"))

    # produto tem ordem: id, nome, quantidade, estoque_minimo
    old_q = produto[2]
    delta = old_q - new_q

    produto_id = produto[0]

    # registrar movimentação conforme variação
    if delta > 0:
        cursor.execute(
            "INSERT INTO movimentacoes (produto_id, tipo, quantidade, usuario_id) VALUES (?, 'saida', ?, 1)",
            (produto_id, delta),
        )
    elif delta < 0:
        cursor.execute(
            "INSERT INTO movimentacoes (produto_id, tipo, quantidade, usuario_id) VALUES (?, 'entrada', ?, 1)",
            (produto_id, -delta),
        )

    cursor.execute(
        "UPDATE produtos SET quantidade = ? WHERE id = ?",
        (new_q, produto_id),
    )

    conn.commit()
    conn.close()

    flash("Atualização semanal salva")
    return redirect(url_for("estoque"))

@app.route("/historico_movimentacoes")
def historico_movimentacoes():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT m.id, p.nome, m.tipo, m.quantidade, m.data AS data_hora
        FROM movimentacoes m
        JOIN produtos p ON m.produto_id = p.id
        ORDER BY m.data DESC
    """)
    movimentacoes = cursor.fetchall()

    conn.close()
    return render_template("historico_movimentacoes.html", movimentacoes=movimentacoes)


if __name__ == "__main__":
    app.run(debug=True)