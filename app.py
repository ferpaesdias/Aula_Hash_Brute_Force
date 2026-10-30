# ============================================================
#  SISTEMA CRUD SIMPLES - "Cadastro de Clientes"
#  Alvo do laboratório de Ataque de Força Bruta (UC13)
#
#  Este sistema é PROPOSITALMENTE vulnerável e serve apenas
#  para uso em ambiente controlado de sala de aula.
#  NÃO use nada disto em produção.
# ============================================================

import sqlite3
import hashlib
from flask import (Flask, request, redirect, url_for,
                   session, render_template_string)

from config import MODO_SENHA, MSG_FALHA, PORTA, SECRET_KEY, DB_PATH

# bcrypt só é necessário quando MODO_SENHA = "bcrypt"
try:
    import bcrypt
except ImportError:
    bcrypt = None

app = Flask(__name__)
app.secret_key = SECRET_KEY


# ------------------------------------------------------------
#  Funções de banco de dados
# ------------------------------------------------------------
def conectar():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


# ------------------------------------------------------------
#  Verificação da senha de acordo com o modo configurado
# ------------------------------------------------------------
def verificar_senha(senha_digitada, valor_armazenado):
    if MODO_SENHA == "plano":
        return senha_digitada == valor_armazenado

    elif MODO_SENHA == "md5":
        calculado = hashlib.md5(senha_digitada.encode()).hexdigest()
        return calculado == valor_armazenado

    elif MODO_SENHA == "bcrypt":
        if bcrypt is None:
            raise RuntimeError("Instale o bcrypt: pip install bcrypt")
        return bcrypt.checkpw(senha_digitada.encode(),
                              valor_armazenado.encode())

    return False


# ------------------------------------------------------------
#  TEMPLATES (HTML embutido para facilitar a leitura em sala)
# ------------------------------------------------------------
TPL_LOGIN = """
<!doctype html>
<html lang="pt-br">
<head>
  <meta charset="utf-8">
  <title>Sistema de Cadastro - Login</title>
  <style>
    body { font-family: Arial, sans-serif; background:#f0f0f0;
           display:flex; justify-content:center; align-items:center;
           height:100vh; margin:0; }
    .caixa { background:#fff; padding:30px 40px; border:1px solid #ccc;
             border-radius:6px; width:300px; }
    h2 { margin-top:0; }
    input { width:100%; padding:8px; margin:6px 0 14px;
            box-sizing:border-box; }
    button { width:100%; padding:10px; background:#004C94; color:#fff;
             border:0; cursor:pointer; font-size:15px; }
    .erro { background:#ffe0e0; color:#a00000; padding:8px;
            text-align:center; margin-bottom:12px; border:1px solid #a00000; }
  </style>
</head>
<body>
  <form class="caixa" method="POST" action="/login">
    <h2>Acesso ao Sistema</h2>
    {% if erro %}<div class="erro">{{ erro }}</div>{% endif %}
    <label>Usuário</label>
    <input type="text" name="usuario" autofocus>
    <label>Senha</label>
    <input type="password" name="senha">
    <button type="submit">Entrar</button>
  </form>
</body>
</html>
"""

TPL_PAINEL = """
<!doctype html>
<html lang="pt-br">
<head>
  <meta charset="utf-8">
  <title>Painel - Clientes</title>
  <style>
    body { font-family: Arial, sans-serif; margin:0; background:#f5f5f5; }
    header { background:#004C94; color:#fff; padding:14px 24px;
             display:flex; justify-content:space-between; align-items:center; }
    header a { color:#fff; }
    .conteudo { padding:24px; }
    table { border-collapse:collapse; width:100%; background:#fff; }
    th,td { border:1px solid #ccc; padding:8px 10px; text-align:left; }
    th { background:#e8eef6; }
    form.inline { display:inline; }
    .form-novo { background:#fff; border:1px solid #ccc; padding:16px;
                 margin-bottom:20px; max-width:600px; }
    .form-novo input { padding:6px; margin-right:8px; }
    button { background:#004C94; color:#fff; border:0; padding:7px 14px;
             cursor:pointer; }
    .del { background:#a00000; }
  </style>
</head>
<body>
  <header>
    <strong>Sistema de Cadastro de Clientes</strong>
    <span>Logado como: {{ usuario }} &nbsp; | &nbsp;
      <a href="/sair">Sair</a></span>
  </header>
  <div class="conteudo">
    <div class="form-novo">
      <h3>Novo cliente</h3>
      <form method="POST" action="/clientes/novo">
        <input name="nome" placeholder="Nome" required>
        <input name="email" placeholder="E-mail">
        <input name="telefone" placeholder="Telefone">
        <button type="submit">Adicionar</button>
      </form>
    </div>

    <table>
      <tr><th>ID</th><th>Nome</th><th>E-mail</th><th>Telefone</th><th>Ações</th></tr>
      {% for c in clientes %}
      <tr>
        <td>{{ c['id'] }}</td>
        <td>{{ c['nome'] }}</td>
        <td>{{ c['email'] }}</td>
        <td>{{ c['telefone'] }}</td>
        <td>
          <form class="inline" method="POST"
                action="/clientes/excluir/{{ c['id'] }}">
            <button class="del" type="submit">Excluir</button>
          </form>
        </td>
      </tr>
      {% else %}
      <tr><td colspan="5">Nenhum cliente cadastrado.</td></tr>
      {% endfor %}
    </table>
  </div>
</body>
</html>
"""


# ------------------------------------------------------------
#  ROTAS
# ------------------------------------------------------------
@app.route("/")
def raiz():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("usuario", "")
        senha = request.form.get("senha", "")

        con = conectar()
        linha = con.execute(
            "SELECT senha FROM usuarios WHERE usuario = ?", (usuario,)
        ).fetchone()
        con.close()

        if linha and verificar_senha(senha, linha["senha"]):
            session["usuario"] = usuario
            return redirect(url_for("painel"))

        # Falha: devolve a página com a MSG_FALHA (usada pelo Hydra)
        return render_template_string(TPL_LOGIN, erro=MSG_FALHA)

    return render_template_string(TPL_LOGIN, erro=None)


@app.route("/painel")
def painel():
    if "usuario" not in session:
        return redirect(url_for("login"))
    con = conectar()
    clientes = con.execute("SELECT * FROM clientes ORDER BY id").fetchall()
    con.close()
    return render_template_string(TPL_PAINEL,
                                  usuario=session["usuario"],
                                  clientes=clientes)


@app.route("/clientes/novo", methods=["POST"])
def novo_cliente():
    if "usuario" not in session:
        return redirect(url_for("login"))
    con = conectar()
    con.execute(
        "INSERT INTO clientes (nome, email, telefone) VALUES (?, ?, ?)",
        (request.form.get("nome"),
         request.form.get("email"),
         request.form.get("telefone")))
    con.commit()
    con.close()
    return redirect(url_for("painel"))


@app.route("/clientes/excluir/<int:cid>", methods=["POST"])
def excluir_cliente(cid):
    if "usuario" not in session:
        return redirect(url_for("login"))
    con = conectar()
    con.execute("DELETE FROM clientes WHERE id = ?", (cid,))
    con.commit()
    con.close()
    return redirect(url_for("painel"))


@app.route("/sair")
def sair():
    session.clear()
    return redirect(url_for("login"))


# ------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 50)
    print(f"  MODO DE SENHA ATIVO: {MODO_SENHA}")
    print(f"  Acesse em: http://<IP-DESTA-VM>:{PORTA}/")
    print("=" * 50)
    app.run(host="0.0.0.0", port=PORTA, debug=False)
