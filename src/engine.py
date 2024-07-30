import subprocess
import time
import requests

class SGlangEngine:
    def __init__(self, model="meta-llama/Meta-Llama-3-8B-Instruct", host="0.0.0.0", port=30000):
        self.model = model
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}/v1"
        self.process = None

    def start_server(self):
        command = [
            "python3", "-m", "sglang.launch_server",
            "--model", self.model,
            "--host", self.host,
            "--port", str(self.port)
        ]
        self.process = subprocess.Popen(command, stdout=None, stderr=None)
        print(f"Server started with PID: {self.process.pid}")

    def wait_for_server(self, timeout=300, interval=5):
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{self.base_url}/models")
                if response.status_code == 200:
                    print("Server is ready!")
                    return True
            except requests.RequestException:
                pass
            time.sleep(interval)
        raise TimeoutError("Server failed to start within the timeout period.")

    def shutdown(self):
        if self.process:
            self.process.terminate()
            self.process.wait()
            print("Server shut down.")