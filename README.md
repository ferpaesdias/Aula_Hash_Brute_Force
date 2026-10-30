# Laboratório — Ataque de Força Bruta e Armazenamento de Senhas

> **UC13 — Planejar e implementar a criptografia de dados e certificados digitais**
> Técnico em Redes de Computadores — SENAC SP

Atividade prática que demonstra, na mão, **por que o modo de armazenar senhas
importa**. Os alunos atacam um sistema web CRUD propositalmente vulnerável
usando força bruta e observam a diferença entre senhas guardadas em **texto
plano**, em **hash fraco (MD5)** e em **hash forte (bcrypt)**.

---

## ⚠️ Uso restrito a ambiente de laboratório

Todo o material é **deliberadamente inseguro** e existe apenas para fins
didáticos, em rede isolada e com autorização do docente. Executar estas
técnicas contra sistemas de terceiros é crime no Brasil
(Lei 12.737/2012 — "Lei Carolina Dieckmann", e Art. 154-A do Código Penal).

---

## Arquitetura

```
   VM DO PROFESSOR (alvo)                 VMs DOS ALUNOS (atacantes)
   ┌───────────────────────┐             ┌───────────────────────┐
   │ Flask + SQLite        │             │ Kali / Debian         │
   │ Sistema CRUD :5000    │  <───────   │ Hydra  (ataque online)│
   │ sistema.db            │   rede      │ John   (ataque offline)│
   └───────────────────────┘  10.50.44.0/24 └───────────────────────┘
```

## Conteúdo do pacote

| Arquivo | Função |
|---|---|
| `app.py` | Sistema web CRUD (login + cadastro de clientes) — o **alvo** |
| `config.py` | Chave `MODO_SENHA`: `plano` / `md5` / `bcrypt` |
| `init_db.py` | Cria e popula `sistema.db` no formato escolhido |
| `requirements.txt` | Dependências (Flask, bcrypt) |
| `wordlists/usuarios.txt` | Lista de usuários para o Hydra |
| `wordlists/senhas.txt` | Dicionário de senhas (as fracas caem; a do admin não) |
| `crack.py` | Quebrador de dicionário offline, didático (plano B ao John/hashcat) |
| `roteiro-aluno.md` | Passo a passo do aluno |
| `guia-professor.md` | Guia do docente: 3 fases, respostas e mediação |

## Instalação (VM do professor)

Instale o sistema-alvo. **Em Debian/Kali recentes** o `pip` bloqueia instalação
global (erro `externally-managed-environment`, PEP 668). Escolha uma via:

**Via A — pacotes do Debian (mais simples, sem pip):**
```bash
sudo apt update && sudo apt install -y python3-flask python3-bcrypt sqlite3
```

**Via B — ambiente virtual (venv), isolado:**
```bash
sudo apt install -y python3-venv sqlite3
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```
(lembre de `source venv/bin/activate` a cada nova sessão; saia com `deactivate`)

**Via C — forçar (só porque é VM de laboratório, descartável):**
```bash
pip3 install -r requirements.txt --break-system-packages
```

Depois:
```bash
python3 init_db.py        # cria o banco no modo definido em config.py
python3 app.py            # sobe o sistema em 0.0.0.0:5000
```

Descubra o IP da VM (`ip a`) e informe aos alunos. Libere a porta se houver
firewall: `sudo ufw allow 5000/tcp`.

## Usuários pré-cadastrados

| Usuário | Senha | Força |
|---|---|---|
| joao | `123456` | muito fraca |
| maria | `senha` | fraca |
| pedro | `abc123` | fraca |
| ana | `brasil2024` | média |
| admin | *(forte, fora da wordlist)* | forte |

## As 3 fases (trocar `MODO_SENHA` e rodar `init_db.py` de novo)

1. **`plano`** — senha em texto puro. Vazou o banco, vazou tudo.
2. **`md5`** — hash fraco. O banco mostra hashes, mas o MD5 cai rápido no ataque offline (`crack.py`, hashcat ou John jumbo — ver guia do professor, seção 5).
3. **`bcrypt`** — hash forte com salt. Resiste ao ataque offline; só a senha fraca é o problema.
