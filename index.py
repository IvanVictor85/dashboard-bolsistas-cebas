from flask import Flask, Response
import subprocess
import os
import sys

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <html>
    <head>
        <title>Dashboard São Camilo</title>
        <meta http-equiv="refresh" content="0; url=https://dashboard-bolsistas-cebas.streamlit.app/">
    </head>
    <body>
        <h1>Redirecionando para o Dashboard São Camilo...</h1>
        <p>Se não for redirecionado automaticamente, <a href="https://dashboard-bolsistas-cebas.streamlit.app/">clique aqui</a>.</p>
        <p>Este é um aplicativo Streamlit que funciona melhor no Streamlit Cloud.</p>
    </body>
    </html>
    """

@app.route('/health')
def health():
    return {"status": "ok", "message": "Dashboard São Camilo - Streamlit App"}

if __name__ == '__main__':
    app.run(debug=True)