# ============================================================
#  CRIAÇÃO E POPULAÇÃO DO BANCO DE DADOS
#
#  Rode este script SEMPRE que trocar o MODO_SENHA no config.py:
#      python3 init_db.py
#
#  Ele recria o banco "sistema.db" com as senhas no formato
#  escolhido (plano / md5 / bcrypt).
# ============================================================

import sqlite3
import hashlib
import os

from config import MODO_SENHA, DB_PATH

try:
    import bcrypt
except ImportError:
    bcrypt = None


# ------------------------------------------------------------
#  Usuários do sistema (usuário, senha em texto puro)
#
#  As 4 primeiras senhas estão na wordlist -> DEVEM cair no ataque.
#  A senha do "admin" é forte e NÃO está na wordlist -> deve resistir.
# ------------------------------------------------------------
USUARIOS = [
    ("joao",   "123456"),          # muito fraca (numérica)
    ("maria",  "senha"),           # fraca (dicionário)
    ("pedro",  "abc123"),          # fraca
    ("ana",    "brasil2024"),      # média (padrão comum)
    ("admin",  "G7!mX2$kLp9@vQ"),  # FORTE - não está na wordlist
]

# Alguns clientes só para o CRUD ter conteúdo
CLIENTES = [
    ("Carlos Souza",   "carlos@email.com",  "(18) 99111-2233"),
    ("Fernanda Lima",  "fernanda@email.com", "(18) 99222-3344"),
    ("Roberto Alves",  "roberto@email.com",  "(18) 99333-4455"),
]


def transformar(senha):
    """Devolve a senha no formato correto para armazenar no banco."""
    if MODO_SENHA == "plano":
        return senha
    elif MODO_SENHA == "md5":
        return hashlib.md5(senha.encode()).hexdigest()
    elif MODO_SENHA == "bcrypt":
        if bcrypt is None:
            raise SystemExit("Instale o bcrypt:  pip install bcrypt")
        return bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()
    else:
        raise SystemExit(f"MODO_SENHA invalido: {MODO_SENHA}")


def main():
    # Remove banco anterior
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    con = sqlite3.connect(DB_PATH)

    con.execute("""
        CREATE TABLE usuarios (
            id     INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            senha   TEXT NOT NULL
        )""")

    con.execute("""
        CREATE TABLE clientes (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            nome     TEXT NOT NULL,
            email    TEXT,
            telefone TEXT
        )""")

    for usuario, senha in USUARIOS:
        con.execute("INSERT INTO usuarios (usuario, senha) VALUES (?, ?)",
                    (usuario, transformar(senha)))

    for nome, email, tel in CLIENTES:
        con.execute(
            "INSERT INTO clientes (nome, email, telefone) VALUES (?, ?, ?)",
            (nome, email, tel))

    con.commit()
    con.close()

    print("=" * 55)
    print(f"  Banco criado: {DB_PATH}")
    print(f"  MODO_SENHA  : {MODO_SENHA}")
    print(f"  Usuarios    : {len(USUARIOS)}")
    print("=" * 55)
    print("  Para ver como as senhas ficaram armazenadas:")
    print(f'     sqlite3 {DB_PATH} "SELECT usuario, senha FROM usuarios;"')
    print("=" * 55)


if __name__ == "__main__":
    main()
