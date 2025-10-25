from flask import Blueprint, request, jsonify, session
from datetime import date
from models.opiniones import OpinionProducto, OpinionProveedor
from extensions import db

opiniones_bp = Blueprint('opiniones_bp', __name__)


@opiniones_bp.route('/votar', methods=['POST'])
def votar():
    data = request.get_json()
    tipo = data['tipo']  # 'producto' o 'proveedor'
    id_objetivo = int(data['id'])
    comentario = data.get('comentario', '').strip()
    visitante_id = session.get('visitante_id')

    if not visitante_id:
        return jsonify({'error': 'Debes estar logueado para votar'})

    hoy = date.today()

    if tipo == 'producto':
        ya_voto = OpinionProducto.query.filter_by(
            visitante_id=visitante_id,
            producto_id=id_objetivo
        ).filter(OpinionProducto.fecha == hoy).first()

        if ya_voto:
            return jsonify({'error': 'Ya votaste hoy por este producto'})

        nueva = OpinionProducto(
            visitante_id=visitante_id,
            producto_id=id_objetivo,
            calidad=int(data.get('calidad', 0)),
            precio=int(data.get('precio', 0)),
            utilidad=int(data.get('utilidad', 0)),
            presentacion=int(data.get('presentacion', 0)),
            comentario=comentario,
            fecha=hoy
        )
        db.session.add(nueva)

        votos = OpinionProducto.query.filter_by(producto_id=id_objetivo).all()
        promedio = sum(
            (v.calidad + v.precio + v.utilidad + v.presentacion) / 4
            for v in votos
            if all([
                v.calidad is not None,
                v.precio is not None,
                v.utilidad is not None,
                v.presentacion is not None
            ])
        ) / len(votos) if votos else 0

    elif tipo == 'proveedor':
        ya_voto = OpinionProveedor.query.filter_by(
            visitante_id=visitante_id,
            proveedor_id=id_objetivo
        ).filter(OpinionProveedor.fecha == hoy).first()

        if ya_voto:
            return jsonify({'error': 'Ya votaste hoy por este proveedor'})

        nueva = OpinionProveedor(
            visitante_id=visitante_id,
            proveedor_id=id_objetivo,
            atencion=int(data.get('atencion', 0)),
            puntualidad=int(data.get('puntualidad', 0)),
            variedad=int(data.get('variedad', 0)),
            confiabilidad=int(data.get('confiabilidad', 0)),
            comentario=comentario,
            fecha=hoy
        )
        db.session.add(nueva)

        votos = OpinionProveedor.query.filter_by(proveedor_id=id_objetivo).all()
        promedio = sum(
            (v.atencion + v.puntualidad + v.variedad + v.confiabilidad) / 4
            for v in votos
            if all([
                v.atencion is not None,
                v.puntualidad is not None,
                v.variedad is not None,
                v.confiabilidad is not None
            ])
        ) / len(votos) if votos else 0

    db.session.commit()
    return jsonify({'id': id_objetivo, 'promedio': round(promedio, 1)})


@opiniones_bp.route('/votar_caracteristica', methods=['POST'])
def votar_caracteristica():
    data = request.get_json()
    tipo = data['tipo']  # 'producto' o 'proveedor'
    id_objetivo = int(data['id'])
    caracteristica = data['caracteristica']
    comentario = data.get('comentario', '').strip()
    valor = int(data['valor'])
    visitante_id = session.get('visitante_id')

    if not visitante_id:
        return jsonify({'error': 'Debes estar logueado para votar'})

    hoy = date.today()

    if tipo == 'producto':
        opinion = OpinionProducto.query.filter_by(
            visitante_id=visitante_id,
            producto_id=id_objetivo
        ).filter(OpinionProducto.fecha == hoy).first()

        if opinion:
            setattr(opinion, caracteristica, valor)
            if comentario:
                opinion.comentario = comentario
        else:
            opinion = OpinionProducto(
                visitante_id=visitante_id,
                producto_id=id_objetivo,
                fecha=hoy,
                comentario=comentario if comentario else None,
                **{caracteristica: valor}
            )
            db.session.add(opinion)

        votos = OpinionProducto.query.filter_by(producto_id=id_objetivo).all()
        promedio = sum(
            (v.calidad + v.precio + v.utilidad + v.presentacion) / 4
            for v in votos
            if all([
                v.calidad is not None,
                v.precio is not None,
                v.utilidad is not None,
                v.presentacion is not None
            ])
        ) / len(votos) if votos else 0

    elif tipo == 'proveedor':
        opinion = OpinionProveedor.query.filter_by(
            visitante_id=visitante_id,
            proveedor_id=id_objetivo
        ).filter(OpinionProveedor.fecha == hoy).first()

        if opinion:
            setattr(opinion, caracteristica, valor)
            if comentario:
                opinion.comentario = comentario
        else:
            opinion = OpinionProveedor(
                visitante_id=visitante_id,
                proveedor_id=id_objetivo,
                fecha=hoy,
                comentario=comentario if comentario else None,
                **{caracteristica: valor}
            )
            db.session.add(opinion)

        votos = OpinionProveedor.query.filter_by(proveedor_id=id_objetivo).all()
        promedio = sum(
            (v.atencion + v.puntualidad + v.variedad + v.confiabilidad) / 4
            for v in votos
            if all([
                v.atencion is not None,
                v.puntualidad is not None,
                v.variedad is not None,
                v.confiabilidad is not None
            ])
        ) / len(votos) if votos else 0

    db.session.commit()
    return jsonify({'promedio': round(promedio, 1)})