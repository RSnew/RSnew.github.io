#!/usr/bin/env python3
"""Local machine status API for the dashboard. Runs on port 9878."""
import json, os, subprocess, time
from http.server import HTTPServer, BaseHTTPRequestHandler

def get_status():
    try:
        uptime = subprocess.getoutput("uptime | sed 's/.*up //' | sed 's/,.*//'").strip()
        load_raw = subprocess.getoutput("/usr/sbin/sysctl -n vm.loadavg 2>/dev/null").strip()
        load = load_raw.split()[1] if len(load_raw.split()) > 1 else "?"
        mem_raw = subprocess.getoutput("/usr/sbin/sysctl -n hw.memsize 2>/dev/null").strip()
        mem_total = int(mem_raw) // (1024**3) if mem_raw.isdigit() else 24
        disk = subprocess.getoutput("df -h / | tail -1 | awk '{print $4}'").strip()
        cpu = subprocess.getoutput("ps -A -o %cpu | awk '{s+=$1} END {printf \"%.0f\", s}'").strip()
        # Services
        services = {}
        procs = subprocess.getoutput("ps aux")
        services["QQ Bot"] = "nonebot" in procs.lower() or "main.py" in procs
        services["NapCat"] = "napcat" in procs.lower() or "qemu" in procs.lower()
        services["GitHub Runner"] = "Runner.Listener" in procs
        services["Danmaku"] = "danmaku" in procs.lower() or "9877" in procs
        services["PromptCraft"] = "promptcraft" in procs.lower() or "8088" in procs
        return {
            "uptime": uptime, "load": load, "memory_gb": mem_total,
            "disk_free": disk, "cpu_pct": cpu,
            "services": {k: "online" if v else "offline" for k, v in services.items()},
            "updated": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
    except Exception as e:
        return {"error": str(e)}

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/status":
            data = get_status()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode())
        else:
            self.send_error(404)
    def log_message(self, *a): pass

if __name__ == "__main__":
    print("Status API on :9878")
    HTTPServer(("0.0.0.0", 9878), Handler).serve_forever()
