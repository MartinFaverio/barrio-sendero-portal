import pymysql
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path='data.env')

# Obtener credenciales desde .env
user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
db_name = os.getenv('DB_NAME')

# Conexión sin seleccionar base
connection = pymysql.connect(
    host='localhost',
    user=user,
    password=password
)

cursor = connection.cursor()

# Crear base si no existe
cursor.execute(f"""
    CREATE DATABASE IF NOT EXISTS {db_name}
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
""")

print(f"✅ Base de datos '{db_name}' verificada o creada correctamente.")

cursor.close()
connection.close()