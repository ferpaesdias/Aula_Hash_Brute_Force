# ============================================================
#  CONFIGURAÇÃO DO LABORATÓRIO - Ataque de Força Bruta
#  UC13 - Criptografia de Dados e Certificados Digitais
# ============================================================
#
#  Modo de ARMAZENAMENTO das senhas dos usuários no banco.
#  Troque o valor abaixo e rode novamente "python3 init_db.py"
#  para recriar o banco com o novo formato.
#
#     "plano"   -> senha em texto puro               (INSEGURO - Fase 1)
#     "md5"     -> hash MD5 sem salt (hash fraco)     (Fase 2)
#     "bcrypt"  -> hash bcrypt com salt (recomendado) (Fase 3)
#
# ------------------------------------------------------------

MODO_SENHA = "plano"

# String exibida quando o login FALHA.
# O Hydra usa este texto para saber que a tentativa deu errado (parâmetro :F=).
# Mantemos sem acentos de propósito, para facilitar o comando do Hydra.
MSG_FALHA = "ACESSO NEGADO"

# Porta em que o sistema vai rodar.
PORTA = 5000

# Configurações internas (não precisa mexer)
SECRET_KEY = "chave-de-laboratorio-NAO-use-em-producao"
DB_PATH = "sistema.db"
