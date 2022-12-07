import requests

BASE = "http://127.0.0.1:8000/"

s = requests.session()
s.headers = headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

# response = s.post(BASE + "auth/register", json={"username":"ibrahimbuk16", "password":"ibrahim19"})
# print(response.json())
# response = s.post(BASE + "auth/login", json={"username":"ibrahimbuk16", "password":"ibrahim19"})
# print(response.json())
# response = s.post(BASE + "auth/login", json={"username":"ibrahimbuk16", "password":"ibrahim19"})
# print(response.json())
# response = s.get(BASE + "auth/logout")
# print(response.json())



