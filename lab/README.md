# Lab fechado: por que senha fraca cai

Este lab gera um handshake WPA2 **do zero**, com parâmetros que nós escolhemos, e mostra
ele caindo numa quebra offline. **Não há captura de rede real, não há monitor mode, não há
deauth.** O `.cap` é um arquivo de treino, montado com a criptografia de verdade do WPA2.

## Parâmetros do alvo de treino

| Campo | Valor | Observação |
|---|---|---|
| SSID | `CHDEVSEC_LAB` | fictício, nosso |
| BSSID (roteador) | `de:ad:be:ef:13:37` | fictício |
| Cliente | `00:11:22:33:44:55` | fictício |
| Senha | `internet123` | fraca de propósito; está na `wordlist-exemplo.txt` |

Nada disso é de rede real. É tudo escolhido pra demonstração.

## Como funciona o `gen_handshake.py`

Ele reproduz o 4-way handshake do WPA2 em software:

1. Deriva a **PMK** com `PBKDF2-HMAC-SHA1(senha, SSID, 4096 iterações)` — o mesmo cálculo
   que o seu roteador faz.
2. Deriva a **PTK/KCK** com o PRF do 802.11i, usando os MACs e os nonces do lab.
3. Monta os quadros 802.11 (beacon + EAPOL M1/M2) e calcula o **MIC** válido da M2.
4. Escreve `lab.cap` (pcap link-type 105), que `aircrack-ng` e `hcxpcapngtool` leem, e
   também `lab.hc22000` (linha PMKID no formato do hashcat) — assim a quebra roda com
   **hashcat puro, sem precisar de hcxtools** pra converter o `.cap`.

O arquivo prova que a senha certa gera aquele MIC — mas **não contém a senha**. Quem quebra
só consegue porque **testa palpites** e vê qual reproduz o MIC.

## Rodar

```bash
python3 gen_handshake.py        # -> lab.cap
./quebrar.sh                    # quebra com a wordlist de exemplo
```

### Quebra (o que o `quebrar.sh` roda)

O `gen_handshake.py` já escreve o `lab.hc22000`, então basta rodar o modo 22000
(WPA-PBKDF2-PMKID+EAPOL) do hashcat:

```bash
hashcat -m 22000 lab.hc22000 wordlist-exemplo.txt --potfile-path lab.pot
hashcat -m 22000 lab.hc22000 --show --potfile-path lab.pot
```

Alternativas a partir do `.cap` (se preferir): `hcxpcapngtool -o lab.hc22000 lab.cap`
(hcxtools) ou `aircrack-ng -w wordlist-exemplo.txt -b DE:AD:BE:EF:13:37 lab.cap`.

Resultado (verificado com hashcat 7.1.2, modo 22000, backend CPU):

```
...:deadbeef1337:001122334455:CHDEVSEC_LAB:internet123
Status...........: Cracked
Recovered........: 1/1 (100.00%)
```

Caiu na hora porque `internet123` está na lista de 10 senhas comuns. **Essa é a lição.**

## Agora inverta (a parte que importa)

Edite o `PSK` no `gen_handshake.py` para algo **longo e aleatório**, ex.:

```python
PSK = "k7$Rm2p9Qx!v4Lw8zT"   # 18 caracteres, aleatória
```

Rode `python3 gen_handshake.py` de novo e `hashcat -m 22000 lab.hc22000 wordlist-exemplo.txt`.
Ele **não acha**. Essa senha não está em lista nenhuma e testar todas as combinações é
inviável. É exatamente o que a sua rede precisa — ver [`../defesa/README.md`](../defesa/README.md).
