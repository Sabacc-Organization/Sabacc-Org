import requests

# SERVER_IP = (127, 0, 0, 1)
# SERVER_PORT = (5000)
SERVER_URL = "http://127.0.0.1:5000"

print("Hello, world!")
print("Welcome to sabacc! (barebones client)")
print("Choose one of the following options:")
print("1. Register")
print("2. Log In")
print("3. Exit")
print()

a = input(">>")

print()
if a == "1":
    username = input("username: ")
    password1 = input("password: ")
    password2 = input("confirm password: ")

    res = requests.post(SERVER_URL + "/register", json = {"username": username, "password": password1, "confirmPassword": password2})

    if res.ok is True:
        print("ok")
    else:
        print(res.text)

