import subprocess
import time
import sys

print("🚀 Launching Uvicorn FastAPI Server in the background...")
# Send stdout to a dedicated log file to keep the notebook interface clean
with open("server.log", "w") as log_file:
    server_process = subprocess.Popen(
        ["uvicorn", "app:app", "--host", "127.0.0.1", "--port", "8000"],
        stdout=log_file,
        stderr=subprocess.STDOUT
    )

print("⏳ Waiting for initial environment configuration and model VRAM allocation...")
print("*(This may take 1-2 minutes on the first run while files are caching)*")

# Continually scan server logs until it initializes completely
model_loaded = False
for _ in range(60):
    time.sleep(3)
    with open("server.log", "r") as f:
        log_content = f.read()
        if "Application startup complete." in log_content:
            model_loaded = True
            print("✓ Uvicorn server is up and listening on port 8000!")
            break
        elif "Traceback" in log_content or "Error" in log_content:
            print("\n❌ CRITICAL: Server crashed during initialization. Log contents:")
            print(log_content)
            sys.exit(1)

if not model_loaded:
    print("\n⚠ Warning: Server taking too long to report readiness. Attempting tunnel anyway...")

print("\n⚡ Connecting Cloudflare Proxy Tunnel to Local Port 8000...")
tunnel_process = subprocess.Popen(
    ["./cloudflared", "tunnel", "--url", "http://127.0.0.1:8000"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)

# Intercept output buffer lines to find your public TryCloudflare URL
try:
    for line in tunnel_process.stdout:
        if ".trycloudflare.com" in line:
            print("\n" + "═"*60)
            print("🎉 PRODUCTION INFERENCE ENDPOINT REGISTERED SUCCESSFULLY!")
            for word in line.split():
                if "trycloudflare.com" in word:
                    # Isolate clean link address
                    clean_url = word.strip().replace("http://", "https://")
                    print(f"🔗 Target Base URL: {clean_url}")
                    print(f"📡 API POST Endpoint: {clean_url}/v1/generate")
            print("═"*60 + "\n")
            print("👇 Tunnel is active. You can now use this URL from anywhere in the world.")
            break
except KeyboardInterrupt:
    print("Terminating background connection pipelines...")
    tunnel_process.terminate()
    server_process.terminate()