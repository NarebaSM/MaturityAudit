from flask import Flask, render_template, flash, request, redirect, url_for, jsonify, abort, make_response, Response
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import socket
import pandas as pd
import json
import jwt
import datetime
import hashlib
import base64
import re
import io
import json
import statistics
import matplotlib.pyplot as plt
from io import BytesIO
from flask import render_template, send_file
from flask import request, redirect, url_for, render_template, send_file
import json
import plotly.express as px
from collections import Counter


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
            if user['username'] == username or user['email'] == username:
                validate = "yes"
                return user
        if validate == "no":
            return None


def sendMail(email):
    remetente = "no-reply.segma5@change.pass"
    destinatario = email


try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
except:
    ip = "127.0.0.1"
    print(f"!!!error connecting to internet, setting ip localhost!!!")
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
        username = request.form['username'].lower()
        password = request.form['password']

        items = getUserItems(username)
        if not items:
            error_message = "Credenciais Invalidas!"
            return render_template('index.html', error=error_message)
        else:
            user = items['username'].lower()
            mail = items['email'].lower()
            if (username == user or username == mail) and password == items['password']:
                token = generate_token(items['username'], items['secretId'])
                response = make_response(redirect(url_for('forms')))
                response.set_cookie('Authorization', f'Bearer {token}')
                response.set_cookie('username', f'{username}')
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

                print(f"user items payload = {userItems}")

                if request.method == 'POST':
                    usr = request.cookies.get('username')
                    response = make_response(redirect(url_for('submit')))
                    response.set_cookie('username', f"{usr}")
                    return response
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
    respostas = []
    for i in range(29):
        resposta = request.form.get(f'nivel{i}')
        respostas.append(resposta)

    mapeamento = {
        '1': 'Péssimo',
        '2': 'Ruim',
        '3': 'Medio',
        '4': 'Bom',
        '5': 'Excelente'
    }

    cores = ['red', 'orange', 'yellow', 'lightgreen', 'green']

    opcoes = [mapeamento[resp] for resp in respostas if resp in mapeamento]

    count_respostas = Counter(opcoes)

    contagens = [count_respostas[opcao] for opcao in mapeamento.values()]

    total_respostas = sum(contagens)

    porcentagens = [round((contagem / total_respostas) * 100) for contagem in contagens]

    plt.figure(figsize=(10, 6))
    bars = plt.bar(mapeamento.values(), contagens, color=cores)

    for bar, porcentagem in zip(bars, porcentagens):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() - 0.5, f'{porcentagem}%',
                 ha='center', va='bottom', color='black', fontsize=10)

    plt.xlabel('')
    plt.ylabel('Quantidade')
    plt.title('Contagem de Respostas por Opção')

    plt.ylim(0, total_respostas)

    plt.savefig('static/respostas_grafico.png')

    return redirect(url_for('result'))


@app.route('/result')
def result():
    return render_template('result.html')


@app.route('/get_chart')
def get_chart():
    return redirect(url_for('static', filename='respostas_grafico.png'))


@app.route('/download_chart')
def download_chart():
    # Caminho para o arquivo de imagem gerado
    chart_path = 'static/respostas_grafico.png'

    # Retorna o arquivo para download
    return send_file(chart_path, as_attachment=True)


@app.route('/register', methods=['GET'])
def register():
    return render_template('register.html')


@app.route('/registerSub', methods=['POST'])
def registerSub():
    usernameReg = request.form['username'].lower()
    passwordReg = request.form['password']
    emailReg = request.form['email']
    CNPJReg = request.form['CNPJ']
    CNPJReg = re.sub(r'\D', '', CNPJReg)

    if usernameReg and passwordReg and emailReg:
        users_data = {}
        validation = "n"
        with open('pass.json', 'r') as users:
            users_data = json.load(users)
        for user in users_data:
            if user['username'].lower() == usernameReg.lower() or user['email'].lower() == emailReg.lower():
                validation = "s"
        if validation == "s":
            error_message = "Usuario ou Email ja registrado!"
            return render_template('register.html', error=error_message)
        else:
            pass_data = ""
            secret = generate_secret_key(usernameReg, passwordReg)
            with open('pass.json', 'r') as passArq:
                pass_data = json.load(passArq)
            newPass = {"username": f"{usernameReg}", "email": f"{emailReg}", "CNPJ": f"{CNPJReg}",
                       "password": f"{passwordReg}", "secretId": f"{secret}"}
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
    app.run(host=ip, port=9876, debug=True)
