#!/usr/bin/env python3
import sys
import argparse
import os
import subprocess

# Încercăm să importăm passlib pentru hashing modern
try:
    from passlib.hash import sha512_crypt, sha256_crypt, md5_crypt, bcrypt
except ImportError:
    print("\n[!] Eroare: Biblioteca 'passlib' nu este instalată.")
    print("[!] Rulează comanda: pip install passlib --break-system-packages\n")
    input("\nApasă Enter pentru a închide...")
    sys.exit(1)

# Culori pentru terminal
GREEN = "\033[92m"
RED = "\033[91m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
RESET = "\033[0m"

BANNER = r"""_                      __  __                 
   / \   __ _ _ __ __ _   |  \/  | __ _ _ __   ___ 
  / _ \ / _` | '__/ _` |  | |\/| |/ _` | '_ \ / _ \
 / ___ \ (_| | | | (_| |  | |  | | (_| | | | |  __/
/_/   \_\__, |_|  \__,_|  |_|  |_|\__,_|_| |_|\___|
        |___/                                      
               [ Version 4.0 - Powered by Nmap ]"""

def display_banner():
    os.system('clear')
    print(f"{BLUE}{BANNER}{RESET}\n")

# --- OPȚIUNEA 1: Scanare Porturi folosind NMAP ---
def scan_ports_nmap(target):
    print(f"\n[*] Se inițiază scanarea {BLUE}Nmap{RESET} (Servicii și OS) pentru: {GREEN}{target}{RESET}")
    print(f"[*] Comandă rulată: nmap -sV -O -F {target}\n")
    
    try:
        # -sV (Detectează versiunile serviciilor), -O (Detectează OS-ul), -F (Scanare rapidă a porturilor comune)
        # Rulează nmap și trimite output-ul direct în terminal în timp real
        result = subprocess.run(
            ["nmap", "-sV", "-O", "-F", target], 
            text=True,
            check=True
        )
    except FileNotFoundError:
        print(f"[{RED}!{RESET}] Eroare: 'nmap' nu este instalat pe acest sistem Kali.")
    except subprocess.CalledProcessError:
        print(f"[{RED}!{RESET}] Eroare: Scanarea Nmap a eșuat. Verifică dacă IP-ul/Domeniul este corect.")
    except KeyboardInterrupt:
        print(f"\n[{RED}!{RESET}] Scanare Nmap întreruptă de utilizator.")
        
    input("\nApasă Enter pentru a reveni la meniu...")

# --- OPȚIUNEA 2: Extragere și Spargere Parolă din /etc/shadow ---
def crack_linux_user(username, wordlist_path):
    if os.geteuid() != 0:
        print(f"[{RED}!{RESET}] Eroare: Această opțiune necesită drepturi de administrator ({RED}sudo{RESET}).")
        input("\nApasă Enter pentru a reveni la meniu...")
        return

    print(f"\n[*] Căutare hash în /etc/shadow pentru utilizatorul: {BLUE}{username}{RESET}")
    target_hash = None

    try:
        with open("/etc/shadow", "r") as f:
            for line in f:
                parts = line.split(":")
                if parts[0] == username:
                    target_hash = parts[1]
                    break
    except Exception as e:
        print(f"[{RED}!{RESET}] Eroare la citirea /etc/shadow: {e}")
        input("\nApasă Enter...")
        return

    if not target_hash or target_hash in ["*", "!", "x", ""]:
        print(f"[{RED}-{RESET}] Utilizatorul nu are un hash valid de parolă configurat sau nu există.")
        input("\nApasă Enter pentru a reveni la meniu...")
        return

    print(f"[{GREEN}+{RESET}] Hash extras cu succes pentru {username}!")
    print(f"[{YELLOW}i{RESET}] Hash-ul complet este: {YELLOW}{target_hash}{RESET}\n")
    
    if not wordlist_path:
        wordlist_path = input("[?] Introdu calea către wordlist (sau lasă gol pentru anulare): ").strip()
        if not wordlist_path:
            return

    if not os.path.exists(wordlist_path):
        print(f"[{RED}!{RESET}] Fișierul wordlist '{wordlist_path}' nu a fost găsit.")
        input("\nApasă Enter...")
        return

    print(f"[*] Se începe atacul de tip Brute-Force...")
    
    crypt_algo = None
    if target_hash.startswith("6"):
        crypt_algo = sha512_crypt
    elif target_hash.startswith("5"):
        crypt_algo = sha256_crypt
    elif target_hash.startswith("1"):
        crypt_algo = md5_crypt
    elif target_hash.startswith("2y") or target_hash.startswith("2b"):
        crypt_algo = bcrypt
    else:
        print(f"[{RED}!{RESET}] Tip de hash nesuportat automat.")
        input("\nApasă Enter...")
        return

    try:
        with open(wordlist_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                password = line.strip()
                if crypt_algo.verify(password, target_hash):
                    print(f"\n[{GREEN}SUCCESS{RESET}] Parolă găsită pentru {username} -> {GREEN}{password}{RESET}")
                    input("\nApasă Enter pentru a reveni...")
                    return
    except KeyboardInterrupt:
        print(f"\n[{RED}!{RESET}] Atac întrerupt.")
        input("\nApasă Enter...")
        return

    print(f"[{RED}-{RESET}] Atac eșuat. Parola nu a fost găsită în wordlist.")
    input("\nApasă Enter pentru a reveni la meniu...")

# --- MENIUL INTERACTIV ---
def interactive_menu():
    while True:
        display_banner()
        print(f"{YELLOW}1.{RESET} Scanare inteligentă de porturi ({BLUE}Nmap OS & Services{RESET})")
        print(f"{YELLOW}2.{RESET} Extragere și spargere parolă utilizator (/etc/shadow)")
        print(f"{YELLOW}3.{RESET} Ieșire")
        
        opțiune = input("\nAlege o opțiune (1-3): ").strip()
        
        if opțiune == "1":
            țintă = input("\n[?] Introdu IP-ul sau domeniul pentru Nmap: ").strip()
            if țintă:
                scan_ports_nmap(țintă)
        elif opțiune == "2":
            utilizator = input("\n[?] Introdu numele utilizatorului Linux: ").strip()
            if utilizator:
                crack_linux_user(utilizator, None)
        elif opțiune == "3":
            print(f"\n{BLUE}[*] La revedere din partea AgraMane!{RESET}")
            sys.exit(0)
        else:
            print(f"\n[{RED}!{RESET}] Opțiune invalidă!")
            import time
            time.sleep(1)

def main():
    if len(sys.argv) == 1:
        interactive_menu()
    else:
        parser = argparse.ArgumentParser(description="AgraMane v4.0")
        group = parser.add_mutually_exclusive_group(required=False)
        group.add_argument('-s', '--scan', metavar='IP')
        group.add_argument('-u', '--user', metavar='USER')
        parser.add_argument('-w', '--wordlist', metavar='FILE')
        args = parser.parse_args()
        
        display_banner()
        if args.scan:
            scan_ports_nmap(args.scan)
        elif args.user:
            crack_linux_user(args.user, args.wordlist)

if __name__ == "__main__":
    main()
