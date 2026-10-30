# Guia do Professor — Ataque de Força Bruta e Armazenamento de Senhas

**UC13 — Criptografia de Dados e Certificados Digitais** · Téc. em Redes · SENAC SP

---

## 1. Para que serve esta atividade (amarração com a UC13)

| Elemento da UC13 (PC 296) | Como a atividade contempla |
|---|---|
| Indicador 2 — criptografar arquivos conforme a necessidade de segurança | O aluno vê, na prática, o que acontece com e sem hash no armazenamento |
| Conhecimento — algoritmos de hash | Contraste direto MD5 (fraco/rápido) × bcrypt (forte/lento com salt) |
| Atitude — sigilo e zelo pela integridade dos dados | O "vazamento" do banco torna concreto o risco de tratar senha como dado comum |
| Habilidade — interpretar textos técnicos e usar termos técnicos | Leitura de saída do Hydra/John e do esquema do banco |

Também serve de insumo para o **PI da UC16** (política de senhas / armazenamento
de credenciais).

**Tempo sugerido:** 1 aula de 3h30 (ou 2 aulas, abrindo a parte offline).

---

## 2. Preparação (uma vez, na sua VM)

```bash
sudo apt update && sudo apt install -y python3-pip sqlite3
pip3 install -r requirements.txt
python3 init_db.py        # começa em MODO_SENHA = "plano"
python3 app.py            # sobe em 0.0.0.0:5000
ip a                      # anote o IP para passar aos alunos
sudo ufw allow 5000/tcp   # se houver firewall
```

As VMs dos alunos (faixa `10.50.44.0/24`) precisam alcançar a sua VM. Teste de
uma máquina de aluno: `curl http://SEU-IP:5000` deve retornar o HTML do login.

> Dica: rode o `app.py` dentro de um `tmux`/`screen`, ou em um segundo
> terminal, para manter o servidor no ar enquanto você mostra o banco.

---

## 3. Roteiro das 3 fases

A troca de fase é **só** mudar `MODO_SENHA` no `config.py` e rodar
`python3 init_db.py` de novo (não precisa reiniciar o `app.py` — ele lê o banco
a cada login; mas reinicie se tiver mudado o modo, pois o `app.py` lê
`MODO_SENHA` na importação). **Recomendado reiniciar o `app.py` a cada troca.**

### FASE 1 — `plano` (texto puro)
1. Alunos fazem o reconhecimento e rodam o Hydra (Partes 0–1 do roteiro).
2. Hydra quebra **joao, maria, pedro, ana**. O **admin resiste**.
3. **Momento-chave:** projete o banco —
   `sqlite3 sistema.db "SELECT usuario, senha FROM usuarios;"`.
   Todas as senhas aparecem **legíveis**. Pergunte: "se este arquivo vaza,
   quantas contas estão comprometidas?" (Resposta: todas as de senha conhecida,
   na hora.)

### FASE 2 — `md5` (hash fraco)
```bash
# no config.py: MODO_SENHA = "md5"
python3 init_db.py && python3 app.py
```
4. Alunos **repetem o mesmo Hydra**. Ele **continua quebrando as senhas fracas**
   — porque o ataque online testa a senha, não o hash. *Esta é a lição que mais
   surpreende a turma.*
5. Mostre o banco de novo: agora são **hashes** (32 caracteres hex), ilegíveis
   a olho nu.
6. Ataque **offline** com John:
   ```bash
   sqlite3 sistema.db "SELECT usuario||':'||senha FROM usuarios;" > hashes.txt
   john --format=Raw-MD5 --wordlist=senhas.txt hashes.txt
   john --show --format=Raw-MD5 hashes.txt
   ```
   As 4 fracas caem **em segundos** (MD5 é rápido). O admin não cai (não está
   na wordlist).

### FASE 3 — `bcrypt` (hash forte com salt)
```bash
# no config.py: MODO_SENHA = "bcrypt"
python3 init_db.py && python3 app.py
```
7. Mostre no banco: cada hash começa com `$2b$12$...` e inclui um **salt**
   diferente — repare que dois usuários com a MESMA senha teriam hashes
   diferentes (pode demonstrar cadastrando dois iguais).
8. Ataque offline de novo:
   ```bash
   sqlite3 sistema.db "SELECT usuario||':'||senha FROM usuarios;" > hashes.txt
   john --format=bcrypt --wordlist=senhas.txt hashes.txt
   ```
   As fracas até caem, mas **muito mais devagar** que no MD5 — o bcrypt é lento
   **de propósito**. Explique o impacto em escala: milhões de tentativas por
   segundo no MD5 × poucos milhares no bcrypt.

> **Fechamento:** o hash protege o **dado armazenado** (se o banco vazar), não
> a conta contra senha fraca no login. Segurança real = **senha forte** +
> **hash lento com salt (bcrypt/argon2)** + **bloqueio de tentativas**.

---

## 4. Gabarito das perguntas do roteiro

- **5/9** — Caem joao, maria, pedro, ana; o admin resiste em todas as fases.
- **7** — Em modo plano, a coluna mostra a senha legível (`123456`, `senha`…).
- **9** — Sim, o Hydra ainda funciona: o ataque online não "vê" o hash, ele só
  manda usuário+senha e observa se entrou. Hash no banco **não** protege contra
  senha fraca no login.
- **10** — As senhas viram hashes ilegíveis.
- **12** — Não impede o ataque online, porque o hash é aplicado no servidor; o
  atacante continua testando senhas de texto. O que muda é a dificuldade de
  **ler** as senhas se o banco vazar.
- **13** — Para proteger as senhas **em repouso**: se o banco for roubado, o
  atacante não tem as senhas prontas, precisa quebrá-las (e, com bcrypt + senha
  forte, pode não conseguir).
- **14** — Porque a senha do admin é **forte e não está na wordlist**; força
  bruta por dicionário só acha o que está na lista; por tentativa exaustiva
  seria inviável no tempo.
- **15** (exemplos aceitáveis) — senhas fortes / política de senhas; hash lento
  com salt (bcrypt ou argon2); bloqueio após N tentativas (lockout) ou
  rate limiting; MFA; CAPTCHA; monitoramento de tentativas; HTTPS.

---

## 5. Extensões opcionais

- **Mitigação na prática:** peça aos alunos para propor (ou você implementa ao
  vivo) um bloqueio após 5 tentativas e refaça o Hydra para mostrar o ataque
  "morrendo".
- **Comparar velocidade:** cronometre o John no MD5 × bcrypt e monte um
  gráfico simples de tentativas/segundo.
- **Discussão de caso real:** vazamentos famosos que guardavam senha em texto
  plano ou MD5 — conectar com a atitude de *sigilo no tratamento de dados*.

## 6. Reset / solução de problemas

- Trocou de modo e deu erro de login? Reinicie o `app.py` (ele lê o modo na
  importação).
- `bcrypt` não encontrado? `pip3 install bcrypt`.
- Quer voltar ao início? Em `config.py` ponha `MODO_SENHA = "plano"` e rode
  `python3 init_db.py`.
