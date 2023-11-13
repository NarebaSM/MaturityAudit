from flask import Flask, render_template, request, redirect, url_for, jsonify, abort, make_response
from flask_cors import CORS
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import datetime
import hashlib
import json
import jwt
import os

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
        validate = "no"
        for user in pass_data:
            if user['username'] == username:
                validate = "yes"
                return user
        if validate == "no":
            return None


def sendMail(email):
    remetente = "no-reply.segma5@change.pass"
    destinatario = email


# s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# s.connect(("8.8.8.8", 80))
# ip = s.getsockname()[0]
# s.close()
app = Flask(__name__)
CORS(app, supports_credentials=True, origins=['auditsegma5.ddns.net', '191.182.179.92:9876'],
     headers=['Content-Type', 'Authorization', 'secret'])
app.config['SESSION_COOKIE_DOMAIN'] = 'auditsegma5.ddns.net'

app.secret_key = 'achavedosucessoeosucesso'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        username = request.form['username']
        password = request.form['password']

        items = getUserItems(username)
        if not items:
            error_message = "Credenciais Invalidas!"
            return render_template('index.html', error=error_message)
        else:
            if username == items['username'] and password == items['password']:
                token = generate_token(items['username'], items['secretId'])
                response = make_response(redirect(url_for('forms')))
                response.set_cookie('Authorization', f'Bearer {token}')
                response.set_cookie('secret', f"{items['secretId']}")
                response.headers['Access-Control-Allow-Credentials'] = 'true'
                return response
            else:
                error_message = "Credenciais Invalidas!"
                return render_template('index.html', error=error_message)


@app.route('/forms', methods=['GET'])
def forms():
    token = request.cookies.get('Authorization')

    if token and token.startswith('Bearer'):
        token = token.split(' ')[1]
        try:

            secretId = request.cookies.get('secret')

            payload = jwt.decode(token, secretId, algorithms=['HS256'])
            if datetime.datetime.utcnow() < datetime.datetime.utcfromtimestamp(payload['exp']):
                username = payload['username']

                userItems = getUserItems(username)

                if request.method == 'POST':
                    return "Respostas enviadas :)"
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

@app.route('/submit', methods=['POST'])
def submit():
    count = 0
    userResp = {}

    while count < 3: #alterar a constante para a quantidade atual de de perguntas
        userResp[f"questao{count}"] = request.form.get(f"nivel{count}")
        count = count + 1

    existing_data = {}
    if os.path.exists('response.json'):
        with open('response.json', 'r') as file:
            existing_data = json.load(file)

    if not isinstance(existing_data, dict):
        existing_data = {}

    for key, value in userResp.items():
        existing_data[key] = value


    with open('response.json', 'w') as file:
        json.dump(existing_data, file)

    print(f"Respostas salvas: {existing_data}")

    return redirect(url_for('chart'))

@app.route('/register', methods=['GET'])
def register():
    return render_template('register.html')


def generate_chart():

    existing_data = {}
    if os.path.exists('response.json'):
        with open('response.json', 'r') as file:
            existing_data = json.load(file)

    counts = {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0}
    total_responses = 0

    for key, value in existing_data.items():
        if key.startswith('questao') and value in counts:
            counts[value] += 1
            total_responses += 1

    averages = {k: v / total_responses for k, v in counts.items()}

    # Gerar gráfico de barras
    plt.bar(averages.keys(), averages.values())
    plt.xlabel('Nota')
    plt.ylabel('Frequência Média')
    plt.title('Média de Notas')

    # Converter a imagem em formato base64
    img_data = BytesIO()
    plt.savefig(img_data, format='png')
    img_data.seek(0)
    img_base64 = base64.b64encode(img_data.read()).decode('utf-8')

    return img_base64


@app.route('/chart')
def chart():
    img_base64 = generate_chart()
    return render_template('chart.html', img_base64=img_base64)

@app.route('/registerSub', methods=['POST'])
def registerSub():
    usernameReg = request.form['username']
    passwordReg = request.form['password']
    emailReg = request.form['email']

    if usernameReg and passwordReg and emailReg:
        users_data = {}
        validation = "n"
        with open('pass.json', 'r') as users:
            users_data = json.load(users)
        for user in users_data:
            if user['username'] == usernameReg or user['email'] == emailReg:
                validation = "s"
        if validation == "s":
            error_message = "Usuario ou Email ja registrado!"
            return render_template('register.html', error=error_message)
        else:
            pass_data = ""
            secret = generate_secret_key(usernameReg, passwordReg)
            with open('pass.json', 'r') as passArq:
                pass_data = json.load(passArq)
            newPass = {"username": f"{usernameReg}", "email": f"{emailReg}", "password": f"{passwordReg}",
                       "secretId": f"{secret}"}
            pass_data.append(newPass)
            with open('pass.json', 'w') as wPass:
                json.dump(pass_data, wPass, indent=4)
    success_message = "Register success"
    return render_template('index.html', successReg=success_message)


@app.route('/changePass', methods=['GET', 'POST'])
def changePass():
    if request.method == 'GET':
        return render_template('changePass.html')
    elif request.method == 'POST':
        email = request.form['email']
        print(f"email = {email}")
        with open('pass.json', 'r') as arq:
            users = json.load(arq)
        for user in users:
            print(f"user email = {user['email']}")
            if user['email'] == email:
                sendMail(email)
                mailMessage = 'Password reset sent to your email.'
                return render_template('changePass.html', mailMessage=mailMessage)
            else:
                return render_template('changePass.html', emailErr='Email não encontrado.')
    else:
        abort(404, description='Method not supportable')


@app.route('/users/list', methods=['GET'])
def users():
    auth = request.headers.get("Authorization")
    if auth == "Bearer YWRtaW46U2VuaGFBZG1pbjEyMzQ1NiFAIyQl==":
        onlyUser = []
        with open('pass.json', 'r') as arq:
            users = json.load(arq)
            for user in users:
                obj = {
                    "username": f"{user['username']}",
                    "email": f"{user['email']}"
                }
                onlyUser.append(obj)
        print(f"only users = {onlyUser}")
        return jsonify(onlyUser)
    else:
        abort(403, description="Unauthorized to user this!")


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=9876, debug=True)
