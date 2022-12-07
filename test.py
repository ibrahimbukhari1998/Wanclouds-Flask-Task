import requests

BASE = "http://127.0.0.1:8000/"

s = requests.session()
s.headers = headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

response = s.post(BASE + "user/register", json={"username":"ibrahimbukhari6", "password":"ibrahim19"})

print(response.json())
