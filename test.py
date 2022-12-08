import requests

BASE = "http://127.0.0.1:8000/"

test = requests.session()
test.headers = headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

# Create a New User
response = test.post(BASE + "auth/register", json={"username":"Testing123", "password":"testing123"})
print("Create a New User:\n", response.json())

# Login to the newly created user
response = test.post(BASE + "auth/login", json={"username":"Testing123", "password":"testing123"})
print("Login:\n", response.json())

# Try to Login Again while already logged in
response = test.post(BASE + "auth/login", json={"username":"Testing123", "password":"testing123"})
print("Login:\n", response.json())

# Start the Sync of data
response = test.get(BASE + "sync")
print("Total Cars entered", response.json())

# Query Cars according ot Make Model and Year
response = test.get(BASE + "car/Civic/2022")
print("Search Query:\n", response.json())

# Logout 
response = test.get(BASE + "auth/logout")
print("Logout:\n", response.json())





