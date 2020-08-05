import requests

cred = {
    'email':'troyabeltran@yahoo.es',
    'password':'mt'
}

login = 'http://192.168.100.105:5000/login'
api = 'http://192.168.100.105:5000/users'

res = requests.post(login,json=cred)
token = res.json().get('token')
print(token)
if token:
    headers = {'Authorization':f'Bearer{token}'}
    print(headers)
    res = requests.get(api,headers=headers)
    print("bien")
else:
    print ("mal")