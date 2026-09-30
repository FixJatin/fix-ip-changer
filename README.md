# fix-ip-changer

A simple tool that automatically changes your Tor IP address every N seconds. You choose the interval.

It works by restarting the Tor service, which gives you a fresh exit IP. No Tor config editing needed.

## Quick start (Kali Linux)

```bash
git clone https://github.com/FixJatin/fix-ip-changer.git
cd fix-ip-changer
sudo apt install tor python3-requests python3-socks -y
sudo python3 ip_changer.py
```

That's it. The tool shows a banner and asks how often (in seconds) you want the IP to change. Press `Ctrl + C` to stop.

## Options

```bash
sudo python3 ip_changer.py -i 60          # change every 60 seconds
sudo python3 ip_changer.py -i 20 -r 60    # random wait between 20 and 60 seconds
sudo python3 ip_changer.py -i 30 -n 10    # change 10 times, then stop
```

| Option | Description | Default |
|---|---|---|
| `-i`, `--interval` | Seconds between IP changes (minimum 5) | asks you |
| `-r`, `--random-max` | Upper bound for a random interval | off |
| `-n`, `--count` | Number of changes (0 = until Ctrl+C) | 0 |

Skip the question by passing the interval directly, e.g. `sudo python3 ip_changer.py -i 30`.

Example output:

```
[*] Your Tor version is: 0.4.8.10
[*] Your current IP address is: 103.xxx.xxx.xxx
[>] How often do you want to change your IP? (in seconds) » 30
[!] Your IP address will be changed every 30 seconds until you stop the script!
[+] #1 Your IP has been changed to 185.220.101.110 (Germany)
[*] Next IP change in  28s
```

## Use it in your browser

The script only changes the Tor IP. Point your browser at Tor's proxy to see it:

1. Firefox: Settings, Network Settings, Manual proxy
2. SOCKS Host `127.0.0.1`, Port `9050`, SOCKS v5
3. Enable "Proxy DNS when using SOCKS v5"
4. In `about:config`, set `media.peerconnection.enabled` to `false` (stops WebRTC leaks)

Check at https://check.torproject.org

## Notes

- Needs `sudo` because it restarts the Tor service.
- The Tor service is stopped when you exit the script with `Ctrl + C`.
- The country next to the IP comes from a free lookup service and may be missing sometimes.
- Each restart briefly drops the Tor connection, so downloads and logged-in sessions may break.
- Tor sometimes gives the same IP twice. The script tells you when that happens.
- Tor Browser uses its own Tor (port 9150) and is not affected. Use Firefox with the proxy above.
- Many websites block Tor exit IPs.

## Disclaimer

For privacy, testing and educational use only. Use it legally and responsibly. The author is not responsible for misuse.

## License

MIT, see [LICENSE](LICENSE).

## Author

[FixJatin](https://github.com/FixJatin)
