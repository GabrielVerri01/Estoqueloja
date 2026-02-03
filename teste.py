import sqlite3

conexao = sqlite3.connect("estoque.db")
cursor = conexao.cursor()

cursor.execute("""
INSERT INTO produtos (nome, codigo, categoria, quanntidade_inicial, estoque_minimo, preco_custo, preco_venda)
VALUES (?, ?, ?, ?, ?, ?)
""", ("Feijão 1kg", "FEJ001", "Alimentos", 10, 5, 7.50, 10.00))

conexao.commit()
conexao.close()

print("Produto inserido!")