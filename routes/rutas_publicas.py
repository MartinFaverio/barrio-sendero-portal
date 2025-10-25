from flask import Blueprint, render_template, request
from models.proveedor import Proveedor
from models.rubro import Rubro
from datetime import datetime, timedelta
from utils.rubro_iconos import rubro_iconos

publicas_bp = Blueprint('publicas_bp', __name__)

@publicas_bp.route('/')
def index():
    cinco_dias = datetime.now() - timedelta(days=5)
    nuevos_proveedores = Proveedor.query.filter(Proveedor.fecha_registro >= cinco_dias).all()

    return render_template(
        'index.html',
        nuevos_proveedores=nuevos_proveedores,
        rubro_iconos=rubro_iconos  # ✅ Pasaje al template
    )


@publicas_bp.route('/buscar_por_rubro')
def buscar_por_rubro():
    rubros = Rubro.query.order_by(Rubro.nombre.asc()).all()
    return render_template('buscar_por_rubro.html', rubros=rubros)


@publicas_bp.route('/resultado_rubro')
def resultado_rubro():
    rubro_nombre = request.args.get('rubro')
    proveedores = Proveedor.query.join(Rubro).filter(Rubro.nombre == rubro_nombre).all()

    proveedores_con_iconos = []
    for proveedor in proveedores:
        rubro = proveedor.rubro.nombre
        icono_info = rubro_iconos.get(rubro, {'icono': 'bi-shop', 'color': 'text-muted'})
        proveedores_con_iconos.append({
            'proveedor': proveedor,
            'icono': icono_info['icono'],
            'color': icono_info['color']
        })

    return render_template('resultado_rubro.html', proveedores=proveedores_con_iconos, rubro=rubro_nombre)


@publicas_bp.route('/emergencias')
def ver_emergencias():
    proveedores = Proveedor.query.filter_by(emergencia=True).order_by(Proveedor.nombre.asc()).all()

    proveedores_con_iconos = []
    for proveedor in proveedores:
        rubro = proveedor.rubro.nombre
        icono_info = rubro_iconos.get(rubro, {'icono': 'bi-shop', 'color': 'text-muted'})
        proveedores_con_iconos.append({
            'proveedor': proveedor,
            'icono': icono_info['icono'],
            'color': icono_info['color']
        })

    return render_template('emergencias.html', proveedores=proveedores_con_iconos)


@publicas_bp.route('/atencion_24hs')
def ver_24hs():
    proveedores = Proveedor.query.filter_by(atencion_24hs=True).order_by(Proveedor.nombre.asc()).all()

    proveedores_con_iconos = []
    for proveedor in proveedores:
        rubro = proveedor.rubro.nombre
        icono_info = rubro_iconos.get(rubro, {'icono': 'bi-shop', 'color': 'text-muted'})
        proveedores_con_iconos.append({
            'proveedor': proveedor,
            'icono': icono_info['icono'],
            'color': icono_info['color']
        })

    return render_template('atencion_24hs.html', proveedores=proveedores_con_iconos)