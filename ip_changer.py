#!/usr/bin/env python3
"""fix-ip-changer: Tor ko restart karke har N second baad naya IP leta hai."""

import argparse
import os
import random
import re
import subprocess
import sys
import time

import requests

VERSION = "1.1"
AUTHOR = "Tom"
GITHUB = "https://github.com/tom0ps"

PROXIES = {
    "http": "socks5h://127.0.0.1:9050",
    "https": "socks5h://127.0.0.1:9050",
}

# ---------- colors ----------
USE_COLOR = sys.stdout.isatty()


def c(code):
    return f"\033[{code}m" if USE_COLOR else ""


ORANGE, GREEN, CYAN = c("38;5;208"), c("92"), c("96")
RED, YELLOW, BOLD, RESET = c("91"), c("93"), c("1"), c("0")


def info(msg):
    print(f"{CYAN}{BOLD}[*]{RESET} {CYAN}{msg}{RESET}")


def ok(msg):
    print(f"{GREEN}{BOLD}[+]{RESET} {GREEN}{msg}{RESET}")


def warn(msg):
    print(f"{ORANGE}{BOLD}[!]{RESET} {ORANGE}{msg}{RESET}")


def err(msg):
    print(f"{RED}{BOLD}[-]{RESET} {RED}{msg}{RESET}")


# ---------- banner ----------
FONT = {
    "T": ["████████╗", "╚══██╔══╝", "   ██║   ", "   ██║   ", "   ██║   ", "   ╚═╝   "],
    "O": [" ██████╗ ", "██╔═══██╗", "██║   ██║", "██║   ██║", "╚██████╔╝", " ╚═════╝ "],
    "M": ["███╗   ███╗", "████╗ ████║", "██╔████╔██║", "██║╚██╔╝██║", "██║ ╚═╝ ██║", "╚═╝     ╚═╝"],

    "I": ["██╗", "██║", "██║", "██║", "██║", "╚═╝"],
    "P": ["██████╗ ", "██╔══██╗", "██████╔╝", "██╔═══╝ ", "██║     ", "╚═╝     "],

    "C": [" ██████╗", "██╔════╝", "██║     ", "██║     ", "╚██████╗", " ╚═════╝"],
    "H": ["██╗  ██╗", "██║  ██║", "███████║", "██╔══██║", "██║  ██║", "╚═╝  ╚═╝"],
    "A": [" █████╗ ", "██╔══██╗", "███████║", "██╔══██║", "██║  ██║", "╚═╝  ╚═╝"],
    "N": ["███╗   ██╗", "████╗  ██║", "██╔██╗ ██║", "██║╚██╗██║", "██║ ╚████║", "╚═╝  ╚═══╝"],
    "G": [" ██████╗ ", "██╔════╝ ", "██║  ███╗", "██║   ██║", "╚██████╔╝", " ╚═════╝ "],
    "E": ["███████╗", "██╔════╝", "█████╗  ", "██╔══╝  ", "███████╗", "╚══════╝"],
    "R": ["██████╗ ", "██╔══██╗", "██████╔╝", "██╔══██╗", "██║  ██║", "╚═╝  ╚═╝"],

    " ": ["   "] * 6,
}


def render(text):
    rows = []
    for r in range(6):
        rows.append("".join(FONT[ch][r].ljust(len(FONT[ch][0])) for ch in text))
    return rows


def box(text):
    w = len(text) + 2
    return [f"╔{'═' * w}╗", f"║ {text} ║", f"╚{'═' * w}╝"]


def print_header():
    os.system("clear" if os.name != "nt" else "cls")
    print()
    for line in render("TOM IP CHANGER"):
        print(f"  {ORANGE}{BOLD}{line}{RESET}")
    print()
    left, right = box(f"Version: {VERSION}"), box(f"Code Author: {AUTHOR}")
    for a, b in zip(left, right):
        print(f"    {CYAN}{a}{RESET}        {CYAN}{b}{RESET}")
    print(f"\n    {ORANGE}{BOLD}GitHub Profile :{RESET} {GREEN}{GITHUB}{RESET}\n")


# ---------- helpers ----------
def get_ip(use_tor=True, timeout=10):
    try:
        r = requests.get(
            "https://api.ipify.org",
            timeout=timeout,
            proxies=PROXIES if use_tor else None,
        )
        r.raise_for_status()
        ip = r.text.strip()
        return ip if re.fullmatch(r"(?:\\d{1,3}\\.){3}\\d{1,3}", ip) else None
    except requests.RequestException:
        return None


def get_country(ip):
    try:
        r = requests.get(
            f"https://ipapi.co/{ip}/country_name/",
            proxies=PROXIES,
            timeout=8,
        )
        r.raise_for_status()
        country = r.text.strip()
        return country if country and len(country) < 80 else None
    except requests.RequestException:
        return None


def tor_version():
    try:
        out = subprocess.run(["tor", "--version"], capture_output=True, text=True).stdout
        m = re.search(r"version\s+([\d.]+\d)", out)
        return m.group(1) if m else None
    except FileNotFoundError:
        return None


def systemctl(action):
    for cmd in (["systemctl", action, "tor"], ["service", "tor", action]):
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    return False


def tor_running():
    for name in ("tor@default", "tor"):
        try:
            if subprocess.run(["systemctl", "is-active", "--quiet", name]).returncode == 0:
                return True
        except FileNotFoundError:
            break
    return False


def wait_for_ip(max_wait=90):
    end = time.time() + max_wait
    while time.time() < end:
        ip = get_ip()
        if ip:
            return ip
        time.sleep(3)
    return None


def countdown(seconds):
    for left in range(seconds, 0, -1):
        sys.stdout.write(f"\r{CYAN}{BOLD}[*]{RESET} {CYAN}Next IP change in {left:>3}s{RESET}   ")
        sys.stdout.flush()
        time.sleep(1)
    sys.stdout.write("\r" + " " * 45 + "\r")
    sys.stdout.flush()


def ask_interval():
    while True:
        try:
            raw = input(f"{GREEN}{BOLD}[>]{RESET} {GREEN}How often do you want to change your IP? "
                        f"(in seconds) »{RESET} ").strip()
        except EOFError:
            sys.exit(1)
        if raw.isdigit() and int(raw) >= 5:
            return int(raw)
        err("Please enter a number (minimum 5 seconds).")


def show_new_ip(count, ip, country):
    extra = f" {YELLOW}({country}){GREEN}" if country else ""
    ok(f"#{count} Your IP has been changed to {BOLD}{ip}{RESET}{GREEN}{extra}")


# ---------- main ----------
def main():
    p = argparse.ArgumentParser(description="Tor IP changer")
    p.add_argument("-i", "--interval", type=int, default=0,
                   help="seconds between IP changes (if not given, it will ask)")
    p.add_argument("-r", "--random-max", type=int, default=0,
                   help="random interval between -i and this value")
    p.add_argument("-n", "--count", type=int, default=0,
                   help="number of changes (0 = until Ctrl+C)")
    args = p.parse_args()

    if os.geteuid() != 0:
        print("[!] Run with sudo:  sudo python3 ip_changer.py")
        sys.exit(1)

    print_header()

    ver = tor_version()
    if not ver:
        err("Tor is not installed. Run:  sudo apt install tor -y")
        sys.exit(1)
    info(f"Your Tor version is: {ver}")
    real_ip = get_ip(use_tor=False)
    info(f"Your current IP address is: {real_ip or 'unknown (no internet?)'}")

    interval = args.interval if args.interval >= 5 else ask_interval()
    if args.random_max and args.random_max < interval:
        err("--random-max must be greater than or equal to the interval.")
        sys.exit(1)

    if args.random_max:
        warn(f"Your IP address will be changed every {interval}-{args.random_max} seconds until you stop the script!")
    else:
        warn(f"Your IP address will be changed every {interval} seconds until you stop the script!")
    warn("Press Ctrl + C to stop.")

    info("Checking for Tor connection...")
    if tor_running():
        info("Restarting Tor service...")
        if not systemctl("restart"):
            err("Could not restart Tor service.")
            sys.exit(1)
    else:
        err("Tor is not running.")
        info("Starting Tor service...")
        if not systemctl("start"):
            err("Could not start Tor service.")
            sys.exit(1)

    done = 0
    last = None
    try:
        while True:
            ip = wait_for_ip()
            if ip:
                done += 1
                show_new_ip(done, ip, get_country(ip))
                if ip == last:
                    warn("Same IP as before, Tor picked the same exit. Trying again next round.")
                last = ip
            else:
                err("Could not get a Tor IP. Check your internet connection.")
            if args.count and done >= args.count:
                break
            wait = random.randint(interval, args.random_max) if args.random_max else interval
            countdown(wait)
            info("Restarting Tor service for the next circuit...")
            if not systemctl("restart"):
                err("Tor restart failed. Stopping safely.")
                break
    except KeyboardInterrupt:
        print()
    warn("Exiting...")
    info("Stopping Tor service...")
    systemctl("stop")


if __name__ == "__main__":
    main()
