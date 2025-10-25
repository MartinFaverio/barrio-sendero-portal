from flask import Blueprint, render_template
from models.proveedor import Proveedor
from utils.rubro_iconos import rubro_iconos

bp_mapa = Blueprint('mapa_bp', __name__)

@bp_mapa.route('/mapa')


def mapa_proveedores():
    proveedores = []

    for p in Proveedor.query.all():
        rubro_nombre = p.rubro.nombre if p.rubro else "Otros"
        icono_data = rubro_iconos.get(rubro_nombre, rubro_iconos["Otros"])

        proveedor_dict = {
            "id": p.id,
            "nombre": p.nombre,
            "latitud": p.latitud,
            "longitud": p.longitud,
            "rubro": rubro_nombre,
            "direccion": p.direccion,
            "emergencia": p.emergencia,
            "atencion_24hs": p.atencion_24hs,
            "icono": icono_data["icono"],
            "color": icono_data["color"]
        }

        proveedores.append(proveedor_dict)

    rubros = sorted(set(p["rubro"] for p in proveedores))

    return render_template("mapa_proveedores.html", proveedores=proveedores, rubros=rubros)
