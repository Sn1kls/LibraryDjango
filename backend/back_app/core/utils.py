import requests


def get_ngrok_url():
    try:
        response = requests.get("http://ngrok:4040/api/tunnels")
        response.raise_for_status()
        data = response.json()

        for tunnel in data.get("tunnels", []):
            if tunnel["public_url"].startswith("https://"):
                return tunnel["public_url"]

        return "http://localhost:8000"
    except Exception as e:
        print(f"Error getting ngrok url: {e}")
        return "http://localhost:8000"
