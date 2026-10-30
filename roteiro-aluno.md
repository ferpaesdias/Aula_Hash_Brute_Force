# Roteiro do Aluno — Ataque de Força Bruta e Armazenamento de Senhas

**UC13 — Criptografia de Dados e Certificados Digitais**
Técnico em Redes de Computadores — SENAC SP

Aluno(a): ______________________________  Turma: ________  Data: ___/___/_____

---

## ⚠️ Antes de começar — regra de ouro

As técnicas deste laboratório só podem ser usadas **aqui, neste ambiente
controlado e com autorização do professor**. Usar força bruta contra qualquer
sistema que não seja seu, ou sem autorização, é **crime** (Lei 12.737/2012).
Um profissional de segurança usa estas ferramentas para **proteger**, nunca
para invadir.

---

## Objetivo

Descobrir, por força bruta, as credenciais de acesso de um sistema web e, em
seguida, comparar o que acontece quando as senhas desse sistema são guardadas
de três formas diferentes: **texto plano**, **hash MD5** e **hash bcrypt**.

Ao final você deve conseguir explicar, com suas palavras, **por que apenas
"ter senha com criptografia" não basta** para um sistema ser seguro.

## Ambiente

- **Alvo:** sistema web do professor, no endereço `http://__________:5000`
  (anote o IP informado: __________________)
- **Sua máquina:** VM Kali/Debian com `hydra` e `john` instalados.
- Ferramentas, se faltarem: `sudo apt install hydra john`

---

## Parte 0 — Reconhecimento

1. Abra o navegador e acesse `http://IP-DO-PROFESSOR:5000`.
2. Observe a tela de login. Tente entrar com um palpite qualquer
   (ex.: `admin` / `admin`). Que mensagem aparece quando a senha está errada?

   Mensagem de erro observada: _______________________________________

   > 💡 Essa mensagem é a "pista" que diz à ferramenta de ataque que a
   > tentativa **falhou**. Guarde-a.

---

## Parte 1 — Ataque de força bruta ONLINE (Hydra)

O **ataque online** testa combinações direto no formulário de login, como se
alguém digitasse milhares de senhas muito rápido.

3. No terminal da sua VM, entre na pasta com as wordlists e rode:

   ```bash
   hydra -L usuarios.txt -P senhas.txt IP-DO-PROFESSOR -s 5000 \
     http-post-form "/login:usuario=^USER^&senha=^PASS^:F=ACESSO NEGADO"
   ```

   - `-L usuarios.txt` → lista de usuários a testar
   - `-P senhas.txt` → lista de senhas a testar
   - `-s 5000` → porta do sistema
   - `^USER^` e `^PASS^` → onde o Hydra encaixa cada tentativa
   - `F=ACESSO NEGADO` → a mensagem de **falha** (a pista da Parte 0)

4. Anote as credenciais que o Hydra encontrou:

   | Usuário | Senha descoberta |
   |---------|------------------|
   |         |                  |
   |         |                  |
   |         |                  |
   |         |                  |

5. **Quantos usuários caíram? Algum resistiu? Qual?**

   ________________________________________________________________

6. Entre no sistema com uma das credenciais descobertas e confirme que você
   tem acesso ao painel de clientes.

---

## Parte 2 — O "vazamento" do banco de dados

Imagine que o atacante conseguiu uma cópia do banco de dados do sistema
(isso acontece o tempo todo em vazamentos reais). O professor vai mostrar, na
tela, o conteúdo da tabela de usuários:

```bash
sqlite3 sistema.db "SELECT usuario, senha FROM usuarios;"
```

7. **Nesta rodada (modo texto plano), o que aparece na coluna "senha"?**

   ________________________________________________________________

8. Se um atacante tivesse só esse arquivo nas mãos, quanto trabalho ele teria
   para saber a senha de **todos** os usuários?

   ________________________________________________________________

---

## Parte 3 — Agora com HASH (o professor troca o modo)

O professor vai reconfigurar o sistema para guardar as senhas como **hash**
(primeiro MD5, depois bcrypt) e recriar o banco. As senhas dos usuários são
as mesmas — muda só a forma de **guardar**.

### 3a) Repita o ataque ONLINE

9. Rode o **mesmo comando do Hydra** da Parte 1. Ele ainda funciona?

   ( ) Sim, descobriu as mesmas senhas fracas   ( ) Não funcionou mais

   > 💡 Conclusão importantíssima: anote o que isso significa sobre hash x
   > senha fraca no login. ______________________________________________

### 3b) Olhe o banco "vazado" de novo

10. Rode de novo o `SELECT` da Parte 2. O que mudou na coluna "senha"?

    ________________________________________________________________

### 3c) Ataque OFFLINE

Agora o atacante tem os **hashes** e vai tentar quebrá-los no próprio PC,
sem falar com o servidor. Primeiro, exporte os hashes do banco "vazado":

```bash
sqlite3 sistema.db "SELECT usuario||':'||senha FROM usuarios;" > hashes.txt
cat hashes.txt
```

Use **uma** das ferramentas abaixo (seu professor indica qual está disponível
no laboratório):

**Opção 1 — crack.py (funciona em qualquer VM, sem instalar nada):**
```bash
python3 crack.py hashes.txt senhas.txt
```

**Opção 2 — hashcat:**
```bash
hashcat -m 0    -a 0 --username hashes.txt senhas.txt   # MD5
hashcat -m 3200 -a 0 --username hashes.txt senhas.txt   # bcrypt
hashcat --username --show hashes.txt
```

**Opção 3 — John the Ripper (versão "jumbo", como no Kali):**
```bash
john --format=Raw-MD5 --wordlist=senhas.txt hashes.txt   # MD5
john --format=bcrypt  --wordlist=senhas.txt hashes.txt   # bcrypt
john --show hashes.txt
```

> 💡 As três fazem a MESMA coisa: para cada palavra da wordlist, aplicam o
> algoritmo de hash e comparam com o hash vazado. O `crack.py` é "à mão" para
> você ver o mecanismo; hashcat e John são as versões profissionais e
> otimizadas. Repare na **velocidade**: MD5 cai quase instantâneo; bcrypt é
> perceptivelmente mais lento — e isso é proposital.

11. Preencha a comparação:

    | Modo | Hydra (online) quebrou as fracas? | John (offline) foi rápido? | admin caiu? |
    |------|-----------------------------------|----------------------------|-------------|
    | MD5    |  |  |  |
    | bcrypt |  |  |  |

---

## Conclusão (responda com suas palavras)

12. O hash impede o ataque de força bruta **no login (online)**? Por quê?

    ________________________________________________________________

13. Para que serve, então, guardar a senha como hash?

    ________________________________________________________________

14. Por que a senha do `admin` **nunca** foi descoberta em nenhuma fase?

    ________________________________________________________________

15. Liste **três** medidas que, juntas, deixariam este sistema realmente
    seguro:

    1. ____________________________________________________________
    2. ____________________________________________________________
    3. ____________________________________________________________
