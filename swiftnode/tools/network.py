"""
swiftnode/tools/network.py
=========================
Network tools: public IP, ping, LAN scan, speed test.
"""
import subprocess
import platform
import socket
import requests


def get_public_ip() -> str:
    """Returns the public IP address of this device."""
    try:
        # Try multiple services for reliability
        services = [
            "https://api.ipify.org?format=json",
            "https://httpbin.org/ip",
            "https://api4.my-ip.io/ip.json"
        ]
        for service in services:
            try:
                res = requests.get(service, timeout=5)
                data = res.json()
                ip = data.get("ip") or data.get("origin", "").split(",")[0].strip()
                if ip:
                    return f"🌐 **Public IP:** `{ip}`"
            except Exception:
                continue
        return "❌ Could not determine public IP."
    except Exception as e:
        return f"❌ Failed: {str(e)}"


def ping_host(host: str) -> str:
    """Pings a host to check connectivity and latency."""
    try:
        system = platform.system().lower()
        if system == "windows":
            cmd = ["ping", "-n", "4", host]
        else:
            cmd = ["ping", "-c", "4", host]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        output = result.stdout.strip()
        
        if result.returncode == 0:
            return f"✅ **Ping {host}:**\n```\n{output}\n```"
        else:
            return f"❌ **Ping failed ({host}):**\n{result.stderr.strip() or output}"
    except subprocess.TimeoutExpired:
        return f"⏱️ Ping to '{host}' timed out."
    except Exception as e:
        return f"❌ Ping error: {str(e)}"


def scan_lan_devices() -> str:
    """Scans the local network to discover connected devices using ARP."""
    try:
        # Get local IP to determine subnet
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        subnet = ".".join(local_ip.split(".")[:3]) + ".0/24"

        results = [f"🔍 **LAN Scan** (subnet: {subnet})\n📍 Your IP: {local_ip}\n"]

        system = platform.system().lower()
        if system == "windows":
            # Use arp -a which is available everywhere on Windows
            cmd = ["arp", "-a"]
        else:
            cmd = ["arp", "-n"]

        arp_result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        
        devices = []
        for line in arp_result.stdout.split('\n'):
            if '192.168.' in line or '10.' in line or '172.' in line:
                parts = line.split()
                if len(parts) >= 2:
                    ip_part = parts[0].strip("()")
                    mac_part = parts[1] if len(parts) > 1 else "N/A"
                    if ':' in mac_part or '-' in mac_part:
                        try:
                            hostname_res = socket.getfqdn(ip_part)
                        except Exception:
                            hostname_res = "Unknown"
                        devices.append(f"  📱 {ip_part:<18} MAC: {mac_part:<20} Host: {hostname_res}")

        if devices:
            results.append(f"Found {len(devices)} device(s):\n" + "\n".join(devices))
        else:
            results.append("No devices found via ARP. Try pinging broadcast first.")

        return "\n".join(results)
    except Exception as e:
        return f"❌ LAN scan failed: {str(e)}"


def run_speed_test() -> str:
    """Runs an internet speed test."""
    try:
        import speedtest
        st = speedtest.Speedtest()
        st.get_best_server()
        download = st.download() / 1_000_000
        upload = st.upload() / 1_000_000
        ping = st.results.ping
        server = st.results.server.get("name", "Unknown") + ", " + st.results.server.get("country", "")
        return (
            f"⚡ **Speed Test Results:**\n"
            f"├─ 📥 Download: {download:.2f} Mbps\n"
            f"├─ 📤 Upload:   {upload:.2f} Mbps\n"
            f"├─ 📡 Ping:     {ping:.0f} ms\n"
            f"└─ 🌍 Server:   {server}"
        )
    except ImportError:
        return "⚠️ speedtest-cli not installed. Run: pip install speedtest-cli"
    except Exception as e:
        return f"❌ Speed test failed: {str(e)}"
