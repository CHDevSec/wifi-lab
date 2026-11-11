# wifi-lab

Laboratório **fechado** e **educacional** sobre segurança de Wi-Fi WPA2/WPA3, feito pela
[CHDevSec](https://chdevsec.com.br). Serve de material do vídeo "Como hackear o Wi-Fi do
vizinho" (spoiler: não dá pra quebrar a criptografia, quebra-se a **senha fraca**).

O objetivo é um só: mostrar **por que uma senha fraca cai em segundos** e **como se
proteger**. Tudo roda contra um handshake que o próprio lab gera, com parâmetros
escolhidos por nós. **Nada aqui captura, ataca ou toca em rede de terceiro.**

> ⚠️ **Aviso legal.** Invadir dispositivo informático de outra pessoa sem autorização é
> crime no Brasil: **art. 154-A do Código Penal** (redação da **Lei 14.155/2021**),
> **reclusão de 1 a 4 anos, e multa**. Este material é para o **seu próprio lab** e para
> **endurecer a sua própria rede**. Use só onde você tem autorização explícita. Ver
> [`ETICA.md`](ETICA.md).

---

## O que este repo NÃO é

Para deixar claro antes de qualquer coisa:

- ❌ Não captura handshake de rede nenhuma (não usa monitor mode, não usa `airodump-ng`).
- ❌ Não derruba cliente de rede nenhuma (não tem `aireplay-ng`, não tem deauth).
- ❌ Não é um passo a passo pra "testar a senha do vizinho".

O handshake é **sintetizado em software** a partir de parâmetros de treino (SSID, MACs,
nonces e senha que nós escolhemos). É um arquivo de laboratório, equivalente aos arquivos
de teste que acompanham ferramentas de auditoria, só que 100% nosso.

## O que este repo É

1. **`lab/`** — gera um handshake WPA2 válido do lab e mostra ele caindo numa quebra
   offline porque a senha é fraca e está numa lista. É a demonstração do mecanismo.
2. **`defesa/`** — o que importa de verdade: como configurar a **sua** rede pra esse
   ataque ser inviável (senha longa e aleatória, WPS desligado, WPA3, firmware).
3. **`ETICA.md`** — uso autorizado e a base legal.

---

## O mecanismo em uma imagem

```
Senha do Wi-Fi  --PBKDF2(SSID, 4096x)-->  PMK  --4-way handshake-->  prova no .cap
                                                                          |
   lista de senhas  --mesmo cálculo-->  compara  <-----------------------+
                                           |
                        bateu? senha fraca encontrada (offline, sem alertar ninguém)
```

Pontos que o vídeo faz questão de separar:

- **A criptografia (WPA2-AES) não é quebrada.** Ninguém "senta e quebra" a cifra.
- **O ataque é contra a senha.** O handshake é só um arquivo que permite **conferir
  palpites offline**. A senha não está dentro dele.
- **Senha de lista cai na hora.** Senha **longa (12+), aleatória, fora de lista** torna o
  teste inviável. É aí que mora a defesa.

---

## Rodar o lab

Pré-requisitos: `python3` e `hashcat` (opcional: `aircrack-ng`, `hcxtools`).

```bash
cd lab
python3 gen_handshake.py        # gera lab.cap (handshake do CHDEVSEC_LAB)
./quebrar.sh                    # quebra offline com a wordlist de exemplo
```

Saída esperada (a senha de treino `internet123` está na lista, então cai na hora):

```
...:deadbeef1337:001122334455:CHDEVSEC_LAB:internet123
Status...........: Cracked
```

Troque a senha no `gen_handshake.py` por uma **longa e aleatória** e rode de novo: ela não
está em lista nenhuma, e a quebra não acha nada. É a lição inteira em dois comandos.

Detalhes em [`lab/README.md`](lab/README.md).

## Proteger a sua rede

O resumo (completo em [`defesa/README.md`](defesa/README.md)):

1. **Senha de 12+ caracteres, longa e aleatória** (não data, não nome, não padrão de lista).
2. **Desligue o WPS** (PIN é vetor de força bruta).
3. **Use WPA3** se o roteador tiver (WPA3 puro; misto só se algum aparelho antigo exigir).
4. **Atualize o firmware** do roteador.
5. **Rede de convidados** separada pra visitas e IoT.

---

CHDevSec — dev & cybersecurity. Medido, não prometido.
Licença [MIT](LICENSE).
