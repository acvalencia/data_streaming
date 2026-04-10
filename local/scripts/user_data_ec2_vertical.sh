#!/bin/bash
# -----------------------------------------------
# Instala Python 3 y pip en Amazon Linux 2023
# -----------------------------------------------
dnf install -y python3 python3-pip

# -----------------------------------------------
# Instala Flask usando pip
# -----------------------------------------------
pip3 install flask

# -----------------------------------------------
# Crea la aplicación Flask con carga de CPU
# -----------------------------------------------
cat > /home/ec2-user/app.py << 'EOF'
from flask import Flask
import time

app = Flask(__name__)

@app.route('/')
def index():
    return '''
    <html>
    <head>
        <title>Escalabilidad Vertical en EC2</title>
        <style>
            body { font-family: Arial; background-color: #f0f0f0; text-align: center; padding-top: 50px; }
            a { text-decoration: none; font-size: 20px; color: white; background-color: #007bff; padding: 10px 20px; border-radius: 5px; }
            a:hover { background-color: #0056b3; }
        </style>
    </head>
    <body>
        <h1>Servidor activo en EC2</h1>
        <p>Este servidor está ejecutándose en una instancia EC2.</p>
        <a href="/cpu">Generar carga de CPU</a>
    </body>
    </html>
    '''

@app.route('/cpu')
def cpu():
    start = time.time()
    while time.time() - start < 120:
        [x**2 for x in range(10000)]
    return "<h2>Carga de CPU simulada por 2 minutos</h2><a href='/'>Volver</a>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
EOF

# -----------------------------------------------
# Crea un servicio de systemd para la app Flask
# -----------------------------------------------
cat > /etc/systemd/system/flaskapp.service << 'EOF'
[Unit]
Description=Flask App
After=network.target

[Service]
User=ec2-user
WorkingDirectory=/home/ec2-user
ExecStart=/usr/bin/python3 /home/ec2-user/app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# -----------------------------------------------
# Recarga systemd, habilita e inicia el servicio
# -----------------------------------------------
systemctl daemon-reexec
systemctl daemon-reload
systemctl enable flaskapp
systemctl start flaskapp
