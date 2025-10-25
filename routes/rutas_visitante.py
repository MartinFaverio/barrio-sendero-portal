from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.visitante import Visitante
from models.confirmaciones import Confirmacion
from extensions import db
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import uuid
from utils.mail import enviar_mail_confirmacion  # ← función que definiremos
from datetime import datetime


visitante_bp = Blueprint('visitante', __name__)

@visitante_bp.route('/registro_visitante', methods=['GET', 'POST'])
def registro_visitante():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        contraseña = request.form['contraseña']

        existente = Visitante.query.filter_by(email=email).first()
        if existente:
            flash('Ya existe un visitante con ese email.')
            return redirect(url_for('visitante.registro_visitante'))

        hash_pw = generate_password_hash(contraseña)
        nuevo = Visitante(nombre=nombre, email=email, contraseña_hash=hash_pw)
        db.session.add(nuevo)
        db.session.commit()

        token = str(uuid.uuid4())
        confirmacion = Confirmacion(visitante_id=nuevo.id, token=token)
        db.session.add(confirmacion)
        db.session.commit()

        link = url_for('visitante_bp.confirmar', token=token, _external=True)
        enviar_mail_confirmacion(email, link)
        flash('Registro exitoso. Revisá tu correo para confirmar tu cuenta.')
        return redirect(url_for('publicas_bp.index'))

    return render_template('registro_visitante.html')


@visitante_bp.route('/confirmar')
def confirmar():
    token = request.args.get('token')
    confirmacion = Confirmacion.query.filter_by(token=token, confirmado=False).first()

    if not confirmacion:
        flash('Token inválido o ya confirmado.')
        return redirect(url_for('publicas_bp.index'))

    confirmacion.confirmado = True
    confirmacion.visitante.confirmado = True
    db.session.commit()

    flash('Cuenta confirmada. Ya podés dejar opiniones.')
    return redirect(url_for('publicas_bp.index'))


@visitante_bp.route('/login_visitante', methods=['GET', 'POST'])
def login_visitante():
    if request.method == 'POST':
        email = request.form['email']
        contraseña = request.form['contraseña']

        visitante = Visitante.query.filter_by(email=email).first()

        if not visitante or not check_password_hash(visitante.contraseña_hash, contraseña):
            flash('Credenciales incorrectas.')
            return redirect(url_for('visitante.login_visitante'))

        if not visitante.confirmado:
            flash('Debés confirmar tu cuenta antes de ingresar.')
            return redirect(url_for('publicas_bp.index'))

        session['visitante_id'] = visitante.id
        session['visitante_nombre'] = visitante.nombre
        flash(f'Bienvenido, {visitante.nombre} 👋')
        return redirect(url_for('publicas_bp.index'))

    return render_template('login_visitante.html')


@visitante_bp.route('/logout_visitante')
def logout_visitante():
    session.pop('visitante_id', None)
    session.pop('visitante_nombre', None)
    flash('Sesión cerrada correctamente.')
    return redirect(url_for('publicas_bp.index'))


