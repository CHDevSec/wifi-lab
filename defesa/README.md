# Defesa: deixar a sua rede inviável de quebrar

O ataque do lab é um **dicionário offline** contra o handshake: o atacante confere palpites
de senha, sem alertar ninguém, até achar o que reproduz o MIC. Toda a defesa gira em torno
de uma ideia: **fazer o palpite certo não existir em lista nenhuma e ser inviável de
adivinhar.**

## 1. Senha longa e aleatória (a que mais importa)

- **12 caracteres no mínimo** — mire em 16+. Cada caractere a mais multiplica o custo do
  ataque.
- **Aleatória**: não use nome, data de nascimento, telefone, placa, "familia01",
  "brasil2024" nem nada que esteja num padrão de lista.
- Use um **gerenciador de senhas** pra criar e guardar. Exemplo de formato forte:
  `k7$Rm2p9Qx!v4Lw8zT`.
- Por quê funciona: o cálculo por palpite (PBKDF2, 4096 iterações) é lento o bastante pra
  que uma senha longa e aleatória leve um tempo inviável. Uma senha de lista, não — cai na
  hora, como o lab mostra.

> Mito comum: "8 caracteres embaralhados já basta." Para Wi-Fi não é confortável — o WPA2
> testa por palpite mais rápido do que os benchmarks de senha de sistema sugerem. Comprimento
> é a alavanca. 12+ aleatórios.

## 2. Desligue o WPS

O WPS por PIN é um vetor conhecido de força bruta (inclusive o ataque Pixie Dust). Desligar
o WPS fecha esse atalho. Procure por "WPS" nas configurações do roteador e deixe **off**.

## 3. Use WPA3 se o roteador tiver

- **WPA3-Personal** adiciona proteção contra adivinhação de senha (SAE) e dificulta o ataque
  de dicionário offline descrito aqui. Referência:
  [Wi-Fi Alliance – Security](https://www.wi-fi.org/discover-wi-fi/security).
- Prefira **WPA3 puro**. Só use o **modo misto (WPA2/WPA3)** se tiver algum aparelho antigo
  que exija WPA2 — e saiba que, no misto, o WPA2 continua exposto ao ataque.
- WPA3 **não é** "não cai nunca": senha fraca ainda é senha fraca. A regra 1 continua valendo.

## 4. Atualize o firmware do roteador

Falhas de protocolo (ex.: KRACK, 2017) foram corrigidas por atualização. Roteador com
firmware velho acumula vetor. Ative atualização automática se existir, ou verifique no
painel do fabricante a cada poucos meses.

## 5. Rede de convidados separada

Deixe visitas e dispositivos IoT (câmeras, lâmpadas, TV) numa **rede de convidados**
isolada da sua rede principal. Se um aparelho desses for fraco, o estrago fica contido.

## 6. Extras que ajudam

- Troque a **senha padrão do painel** de administração do roteador (admin/admin é alvo).
- Desligue a **administração remota** (WAN) se você não usa.
- Esconder o SSID e filtrar MAC **não** são defesa real contra esse ataque — não dependa
  disso. A senha forte é o que segura.

---

## Checklist rápido

- [ ] Senha do Wi-Fi com 12+ caracteres, aleatória, fora de qualquer lista
- [ ] WPS desligado
- [ ] WPA3 ligado (puro, se possível)
- [ ] Firmware do roteador atualizado
- [ ] Rede de convidados para visitas e IoT
- [ ] Senha do painel admin trocada
- [ ] Administração remota (WAN) desligada

CHDevSec — transformar risco em decisão.
