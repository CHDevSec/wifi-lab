#!/usr/bin/env bash
#
# Quebra o handshake do LAB FECHADO (CHDEVSEC_LAB) gerado por gen_handshake.py.
# Roda 100% offline contra um arquivo que o proprio lab criou. Nao toca em rede nenhuma.
#
# Uso: ./quebrar.sh
set -euo pipefail
cd "$(dirname "$0")"

HASH="lab.hc22000"
CAP="lab.cap"
WORDLIST="wordlist-exemplo.txt"
POT="lab.pot"

if [[ ! -f "$HASH" && ! -f "$CAP" ]]; then
  echo "[!] Nada pra quebrar. Rode primeiro: python3 gen_handshake.py"
  exit 1
fi

# gen_handshake.py ja emite o lab.hc22000 (via PMKID), entao o caminho padrao e hashcat
# puro, sem precisar de hcxtools. Se so existir o .cap, tenta converter com hcxtools.
if [[ ! -f "$HASH" && -f "$CAP" ]] && command -v hcxpcapngtool >/dev/null 2>&1; then
  echo "[*] Convertendo $CAP -> $HASH (hcxtools)"
  hcxpcapngtool -o "$HASH" "$CAP" >/dev/null 2>&1 || true
fi

if command -v hashcat >/dev/null 2>&1 && [[ -f "$HASH" ]]; then
  echo "[*] hashcat -m 22000 (wordlist: $WORDLIST)"
  rm -f "$POT"
  hashcat -m 22000 "$HASH" "$WORDLIST" --potfile-path "$POT" || true
  echo
  echo "[*] Resultado:"
  hashcat -m 22000 "$HASH" --show --potfile-path "$POT"
  exit 0
fi

# Fallback: aircrack-ng direto no .cap
if command -v aircrack-ng >/dev/null 2>&1 && [[ -f "$CAP" ]]; then
  echo "[*] hashcat ausente; usando aircrack-ng no $CAP"
  aircrack-ng -w "$WORDLIST" -b DE:AD:BE:EF:13:37 "$CAP"
  exit 0
fi

echo "[!] Instale hashcat (recomendado) ou aircrack-ng para rodar a quebra."
exit 1
