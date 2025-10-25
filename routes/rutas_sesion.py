from flask import Blueprint, request, redirect, url_for, render_template, session
from models.proveedor import Proveedor

sesion_bp = Blueprint('sesion_bp', __name__)

@sesion_bp.route('/login_proveedor', methods=['GET', 'POST'])
def login_proveedor():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        print("🔍 Email recibido:", email)
        print("🔍 Contraseña recibida:", password)

        proveedor = Proveedor.query.filter_by(email=email).first()

        if proveedor:
            print("✅ Proveedor encontrado:", proveedor.email)
            print("🔐 Hash en base:", proveedor.password_hash)
            resultado = proveedor.check_password(password)
            print("🔐 Resultado check_password:", resultado)

            if resultado:
                session['proveedor_id'] = proveedor.id
                print("✅ Login exitoso. ID:", proveedor.id)
                return redirect(url_for('proveedores_bp.mi_pagina'))
            else:
                print("❌ Contraseña incorrecta")
        else:
            print("❌ No se encontró proveedor con ese email")

        return "⚠️ Email o contraseña incorrectos."

    return render_template('login_proveedor.html')