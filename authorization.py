from flask import Flask, render_template, request, redirect, url_for, jsonify, abort, make_response, Response
import json
import jwt
import datetime
import hashlib
import base64


def generate_token(username, secret):
    expiration_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    payload = {
        'username': username,
        'exp': expiration_time
    }
    token = jwt.encode(payload, secret, algorithm='HS256')
    return token

def generate_secret_key(username, password):
    # Combine username e password para criar uma chave única
    combined_data = f"{username}:{password}"

    # Use hashlib para gerar um hash a partir dos dados combinados
    secret_key = hashlib.sha256(combined_data.encode('utf-8')).hexdigest()
    encoded_secret_key = base64.b64encode(secret_key.encode('utf-8')).decode('utf-8')

    return encoded_secret_key


def getUserItems(username):
    with open('pass.json', 'r') as a:
        pass_data = json.load(a)
        for users in pass_data:
            if users['username'] == username:
                return users
            else:
                return None


app = Flask(__name__)

@app.route('/')
def index():

    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    items = getUserItems(username)
    if username == items['username'] and password == items['password']:
        token = generate_token(items['username'], items['secretId'])
        response = make_response(redirect(url_for('forms')))
        response.set_cookie("Authorization", f"Bearer {token}")
        response.set_cookie("secret", f"{items['secretId']}")
        return response
    else:
        return f"Login Failed :("


@app.route('/forms', methods=['GET', 'POST'])
def forms():

    token = request.cookies.get("Authorization")

    if token and token.startswith('Bearer'):
        token = token.split(' ')[1]
        try:

            secretId = request.cookies.get('secret')

            payload = jwt.decode(token, secretId, algorithms=['HS256'])
            if datetime.datetime.utcnow() < datetime.datetime.utcfromtimestamp(payload['exp']):
                username = payload['username']

                userItems = getUserItems(username)

                if request.method == 'POST':
                    q1 = request.form['question1']

                    questoes = {}

                    for questao in request.form:
                        print(f"questao {questao}")

                    user_responses = {
                        f"{username}": {
                        }
                    }
                elif request.method == 'GET':
                    return render_template('forms.html')
                else:
                    abort(404, description="Não consegui fazer nada :(")
        except jwt.ExpiredSignatureError:
            abort(401, description="Token expirado. Faça login novamente.")
        except jwt.InvalidTokenError:
            abort(401, description="Token inválido. Faça login novamente.")
    else:
        abort(401, description="Token não fornecido. Faça login primeiro.")

@app.route('/register', methods=['GET'])
def register():
    return render_template('register.html')

@app.route('/registerSub', methods=['POST'])
def registerSub():
    usernameReg = request.form['username']
    passwordReg = request.form['password']

    if usernameReg != "" and passwordReg != "" and usernameReg != None and passwordReg != None:
        users_data = {}
        validation = "n"
        with open('users.json', 'r') as users:
            users_data = json.load(users)
        for user in users_data:
            if user['username'] == usernameReg:
                validation = "s"
        if validation == "s":
            return 'Usuario ja registrado'
        else:
            newUser = {"username": f"{usernameReg}"}
            users_data.append(newUser)
            pass_data = ""
            secret = generate_secret_key(usernameReg, passwordReg)
            with open('pass.json', 'r') as passArq:
                pass_data = json.load(passArq)
            newPass = {"username": f"{usernameReg}", "password": f"{passwordReg}", "secretId": f"{secret}"}
            pass_data.append(newPass)
            with open('users.json', 'w') as a:
                json.dump(users_data, a, indent=4)
            with open('pass.json', 'w') as wPass:
                json.dump(pass_data, wPass, indent=4)

    return(f'User {usernameReg} registered!\nYou can access the plataform now!')

if __name__ == '__main__':
    app.run(debug=True)
