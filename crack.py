#!/usr/bin/env python3
# ============================================================
#  QUEBRADOR DE DICIONARIO OFFLINE (didatico)
#  UC13 - Criptografia de Dados e Certificados Digitais
#
#  Faz o mesmo que John/hashcat no ataque offline, mas escrito
#  a mao para o aluno ENXERGAR o mecanismo: para cada palavra da
#  wordlist, aplica o mesmo algoritmo de hash e compara com o
#  hash "vazado" do banco.
#
#  Vantagem em sala: nao depende de OpenCL/GPU nem de muita RAM,
#  entao funciona em qualquer VM, inclusive as pequenas.
#
#  Uso:
#     python3 crack.py hashes.txt senhas.txt
#
#  O arquivo de hashes deve ter uma linha por usuario no formato:
#     usuario:hash
#  (foi o que o SELECT ... usuario||':'||senha gerou)
#
#  Detecta automaticamente:
#     - hash que comeca com $2  -> bcrypt
#     - caso contrario          -> MD5 cru (32 hex)
# ============================================================

import sys
import hashlib

try:
    import bcrypt
except ImportError:
    bcrypt = None


def main():
    h_file = sys.argv[1] if len(sys.argv) > 1 else "hashes.txt"
    w_file = sys.argv[2] if len(sys.argv) > 2 else "senhas.txt"

    # Carrega a wordlist
    with open(w_file, encoding="utf-8", errors="ignore") as f:
        senhas = [l.rstrip("\n") for l in f if l.strip()]

    print(f"Wordlist: {w_file}  ({len(senhas)} senhas)")
    print(f"Hashes  : {h_file}\n")

    quebradas = 0
    total = 0

    with open(h_file, encoding="utf-8", errors="ignore") as f:
        for linha in f:
            linha = linha.strip()
            if not linha or ":" not in linha:
                continue
            total += 1
            user, h = linha.split(":", 1)

            achou = None
            if h.startswith("$2"):                     # bcrypt
                if bcrypt is None:
                    print(f"  {user:10} (bcrypt detectado, mas o modulo "
                          f"bcrypt nao esta instalado: pip install bcrypt)")
                    continue
                for s in senhas:
                    if bcrypt.checkpw(s.encode(), h.encode()):
                        achou = s
                        break
            else:                                      # MD5 cru
                for s in senhas:
                    if hashlib.md5(s.encode()).hexdigest() == h:
                        achou = s
                        break

            if achou:
                quebradas += 1
                print(f"  {user:10} => {achou}")
            else:
                print(f"  {user:10} (nao quebrada - fora da wordlist)")

    print(f"\nResultado: {quebradas}/{total} senhas quebradas.")


if __name__ == "__main__":
    main()
