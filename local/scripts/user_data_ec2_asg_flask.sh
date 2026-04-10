#!/bin/bash
# -----------------------------------------------
# Script de inicio para instancias en ASG (Flask)
# Escalabilidad horizontal con ALB 
# -----------------------------------------------

# Instala Python 3 y pip
dnf install -y python3 python3-pip

# Instala Flask
pip3 install flask

# Crea la aplicación Flask que responde en "/"
cat > /home/ec2-user/app.py << 'EOF'
from flask import Flask
import time

app = Flask(__name__)

@app.route('/')
def index():
    return '''
    <html>
    <head>
        <title>Instancia Flask</title>
    </head>
    <body style="font-family:Arial; text-align:center; padding-top:50px;">
        <h2>Instancia activa</h2>
        <a href="/cpu" style="background:#007bff;color:#fff;padding:10px 20px;border-radius:5px;text-decoration:none;">Generar carga de CPU</a>
    </body>
    </html>
    '''

@app.route('/cpu')
def cpu():
    start = time.time()
    while time.time() - start < 300:
        [x**2 for x in range(10000)]
    return "<h3>Carga CPU generada por 2 minutos</h3><a href='/'>Volver</a>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
EOF

# Ejecuta la app Flask como root (puerto 80 requiere privilegios)
nohup python3 /home/ec2-user/app.py &
