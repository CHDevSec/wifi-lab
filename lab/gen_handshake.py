#!/usr/bin/env python3
"""
Gera um handshake WPA2 REAL (4-way, com MIC válido) para a rede de LAB CHDEVSEC_LAB,
num .cap (pcap link-type 105 = IEEE 802.11) que o aircrack-ng e o hcxpcapngtool leem e
quebram de verdade. Nada aqui toca rede real: SSID, MACs, nonces e senha sao do lab,
escolhidos por nos (README.md). A senha esta na wordlist pra demonstrar "senha de lista cai".

Uso:
    python3 gen_handshake.py           # escreve lab.cap ao lado
"""
import struct, hmac, hashlib, os

# --- parametros do lab (os mesmos do README / lab.hc22000) ---
SSID   = b"CHDEVSEC_LAB"
AP_MAC = bytes.fromhex("deadbeef1337")   # BSSID (roteador de treino)
STA_MAC= bytes.fromhex("001122334455")   # cliente de treino
PSK    = "internet123"                    # senha fraca escolhida (esta na wordlist)
# nonces fixos do lab (qualquer valor serve; fixados pra reproducibilidade)
ANONCE = bytes.fromhex("a0" * 32)
SNONCE = bytes.fromhex("5e" * 32)

# --- cripto WPA2 ---
def pmk(psk, ssid):
    return hashlib.pbkdf2_hmac("sha1", psk.encode(), ssid, 4096, 32)

def prf512(key, A, B):
    R = b""
    i = 0
    while len(R) < 64:
        R += hmac.new(key, A + b"\x00" + B + bytes([i]), hashlib.sha1).digest()
        i += 1
    return R[:64]

def ptk(pmk_, aa, spa, anonce, snonce):
    A = b"Pairwise key expansion"
    B = min(aa, spa) + max(aa, spa) + min(anonce, snonce) + max(anonce, snonce)
    return prf512(pmk_, A, B)

# --- montagem 802.11 ---
def dot11(fc0, fc1, a1, a2, a3, seq, body):
    return struct.pack("<BBH", fc0, fc1, 0) + a1 + a2 + a3 + struct.pack("<H", seq) + body

def beacon():
    # timestamp(8) interval(2) cap(2); tags: SSID(0) + RSN(48) p/ aircrack ver WPA2
    fixed = struct.pack("<Q", 0) + struct.pack("<H", 0x0064) + struct.pack("<H", 0x0411)
    ssid_tag = bytes([0, len(SSID)]) + SSID
    rates = bytes([1, 1, 0x82])
    # RSN IE: versao1, CCMP group, 1 pairwise CCMP, 1 akm PSK
    rsn = bytes.fromhex("30140100000fac040100000fac040100000fac020000")
    body = fixed + ssid_tag + rates + rsn
    return dot11(0x80, 0x00, b"\xff"*6, AP_MAC, AP_MAC, 0x0010, body)

def eapol_key(key_info, nonce, mic, key_data=b""):
    # descriptor RSN(0x02); campos conforme 802.11i
    kd  = bytes([0x02])
    kd += struct.pack(">H", key_info)
    kd += struct.pack(">H", 16)            # key length
    kd += struct.pack(">Q", 1)             # replay counter
    kd += nonce                            # 32
    kd += b"\x00"*16                        # key iv
    kd += b"\x00"*8                         # key rsc
    kd += b"\x00"*8                         # key id
    kd += mic                              # 16
    kd += struct.pack(">H", len(key_data)) + key_data
    frame = bytes([0x02, 0x03]) + struct.pack(">H", len(kd)) + kd  # 802.1X: ver,type,len
    return frame

def llc_eapol(payload):
    return bytes.fromhex("aaaa03000000888e") + payload

def data_frame(fromds, a_bssid, a_sta, seq, payload):
    fc1 = 0x02 if fromds else 0x01   # FromDS p/ AP->STA, ToDS p/ STA->AP
    if fromds:
        a1, a2, a3 = a_sta, a_bssid, a_bssid    # DA, BSSID, SA
    else:
        a1, a2, a3 = a_bssid, a_sta, a_bssid    # BSSID, SA, DA
    return dot11(0x08, fc1, a1, a2, a3, seq, llc_eapol(payload))

# --- pcap ---
def pcap(frames):
    # timestamps proximos (dentro de ~100ms) pro aircrack nao estourar o inter-frame timeout
    out = struct.pack("<IHHiIII", 0xa1b2c3d4, 2, 4, 0, 0, 65535, 105)
    for i, f in enumerate(frames):
        out += struct.pack("<IIII", 1700000000, i*15000, len(f), len(f)) + f
    return out

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    PMK = pmk(PSK, SSID)
    PTK = ptk(PMK, AP_MAC, STA_MAC, ANONCE, SNONCE)
    KCK = PTK[:16]

    # M1: AP->STA, ANonce, sem MIC
    m1 = eapol_key(0x008a, ANONCE, b"\x00"*16)
    # M2: STA->AP, SNonce, carrega o RSN IE da estacao no key data (senao vira M4),
    # MIC calculado sobre o proprio frame (key data incluso) com o campo MIC zerado
    rsn_ie = bytes.fromhex("30140100000fac040100000fac040100000fac020000")
    m2_nomic = eapol_key(0x010a, SNONCE, b"\x00"*16, key_data=rsn_ie)
    mic = hmac.new(KCK, m2_nomic, hashlib.sha1).digest()[:16]
    m2 = eapol_key(0x010a, SNONCE, mic, key_data=rsn_ie)

    frames = [
        beacon(),
        data_frame(True,  AP_MAC, STA_MAC, 0x0020, m1),
        data_frame(False, AP_MAC, STA_MAC, 0x0030, m2),
        beacon(),
    ]
    cap = pcap(frames)
    path = os.path.join(here, "lab.cap")
    with open(path, "wb") as fh:
        fh.write(cap)

    # hash direto no formato do hashcat (modo 22000), via PMKID: assim a quebra roda
    # com hashcat puro, sem depender de hcxtools pra converter o .cap.
    pmkid = hmac.new(PMK, b"PMK Name" + AP_MAC + STA_MAC, hashlib.sha1).digest()[:16]
    hc = f"WPA*01*{pmkid.hex()}*{AP_MAC.hex()}*{STA_MAC.hex()}*{SSID.hex()}***"
    hc_path = os.path.join(here, "lab.hc22000")
    with open(hc_path, "w") as fh:
        fh.write(hc + "\n")

    print(f"PMK   = {PMK.hex()}")
    print(f"KCK   = {KCK.hex()}")
    print(f"MIC   = {mic.hex()}")
    print(f"PMKID = {pmkid.hex()}")
    print(f"ok -> {path} ({len(cap)} bytes)")
    print(f"ok -> {hc_path}")

if __name__ == "__main__":
    main()
