from app import app
from extensions import db
from models.rubro import Rubro

with app.app_context():
    db.create_all()

    rubros_iniciales = [
        'Carniceria', 'Panaderia', 'Gastronomia', 'Ferreteria', 'Verduleria',
        'Desayunos', 'Electricidad', 'Escolar', 'Farmacia', 'Libreria',
        'Masajes', 'Otros', 'Peluqueria', 'Perfumeria', 'Salud',
        'Transporte', 'Veterinaria'
    ]

    for nombre in rubros_iniciales:
        if not Rubro.query.filter_by(nombre=nombre).first():
            db.session.add(Rubro(nombre=nombre))

    db.session.commit()

print("✅ Rubros iniciales consagrados correctamente.")
