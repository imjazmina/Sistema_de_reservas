from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///reservas.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = 'mi_clave_secreta'  # Necesario para sesiones y flash messages
db = SQLAlchemy(app)

# Modelo de base de datos
class Reserva(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    hora_entrada = db.Column(db.Time, nullable=False)
    hora_salida = db.Column(db.Time, nullable=False)
    nombre = db.Column(db.String(50), nullable=False)
    correo = db.Column(db.String(100), nullable=False)

# Ruta principal: muestra reservas
@app.route('/')
def index():
    reservas = Reserva.query.order_by(Reserva.fecha).all()
    edit_id = request.args.get('edit_id', type=int)
    reserva_actualizada = Reserva.query.get(edit_id) if edit_id else None
    return render_template('index.html', reservas=reservas, reserva_actualizada=reserva_actualizada)


# Ruta para guardar reserva
@app.route("/reservar", methods=['POST'])
def reservar():
    fecha = datetime.strptime(request.form['fecha'], '%Y-%m-%d').date()
    hora_entrada = datetime.strptime(request.form['hora_entrada'], '%H:%M').time()
    hora_salida = datetime.strptime(request.form['hora_salida'], '%H:%M').time()
    nombre = request.form['nombre']
    correo = request.form['correo']
    if not fecha or not hora_entrada or not hora_salida or not nombre or not correo:
        return redirect(url_for('index', error="Completar todos los campos"))
    elif fecha < datetime.now().date():
        return redirect(url_for('index', error="Fecha inválida"))
    elif hora_entrada >= hora_salida:
        return redirect(url_for('index', error="Hora inválida"))
    reservas = Reserva.query.filter_by(fecha=fecha).all()
    
    # Verificar si el horario ya está reservado solo si ya hay reservas
    if reservas:
        for reserva in reservas:
            if (reserva.hora_entrada <= hora_entrada <= reserva.hora_salida) or (reserva.hora_entrada <= hora_salida <= reserva.hora_salida):
                return redirect(url_for('index', error="Turno reservado"))
    # Si no hay conflictos, guardar la reserva
    nueva_reserva = Reserva(
        fecha=fecha,
        hora_entrada=hora_entrada,
        hora_salida=hora_salida,
        nombre=nombre,
        correo=correo
    )
    db.session.add(nueva_reserva)
    db.session.commit()
    return redirect(url_for('index', error="Reserva realizada con éxito"))

# Ruta para eliminar una reserva
@app.route("/eliminar-reserva/<int:id>", methods=["POST"])
def eliminar_reserva(id):
    reserva = Reserva.query.filter_by(id=id).first()
    if reserva:
        db.session.delete(reserva)
        db.session.commit()
    return redirect(url_for('index', error="Reserva eliminada con éxito"))

def parse_hora(hora_str):
    try:
        return datetime.strptime(hora_str, '%H:%M:%S').time()
    except ValueError:
        return datetime.strptime(hora_str, '%H:%M').time()
# Ruta para editar una reserva

#Ruta para editar los datos de una reserva
@app.route('/actualizar/<int:id>', methods=['POST'])
def actualizar(id):
    reserva_actualizada = Reserva.query.get(id)

    reserva_actualizada.fecha = datetime.strptime(request.form['fecha'], '%Y-%m-%d').date()
    reserva_actualizada.hora_entrada = parse_hora(request.form['hora_entrada'])
    reserva_actualizada.hora_salida = parse_hora(request.form['hora_salida'])
    reserva_actualizada.nombre = request.form['nombre']
    reserva_actualizada.correo = request.form['correo']

    db.session.commit()
    return redirect(url_for('index'))

# Main
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    print("Flask está corriendo en http://127.0.0.1:5000")
    app.run(debug=True)
