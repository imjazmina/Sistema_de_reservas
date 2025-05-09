# --- Importaciones ---
from flask import Flask, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'jazluelronima'
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///reservas.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Modelo de base de datos
class Reserva(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    hora_entrada = db.Column(db.Time, nullable=False)
    hora_salida = db.Column(db.Time, nullable=False)
    materia = db.Column(db.String(50), nullable=False)
    tutor = db.Column(db.String(100), nullable=False)

#ruta de inicio
@app.route('/')
def inicio():
    return render_template('inicio.html')#ruta de inicio

# Ruta principal
@app.route('/index')
def index():
    reservas = Reserva.query.order_by(Reserva.fecha).all()
    edit_id = request.args.get('edit_id', type=int)
    reserva_actualizada = Reserva.query.get(edit_id) if edit_id else None
    return render_template('index.html', reservas=reservas, reserva_actualizada=reserva_actualizada)

@app.route("/reservar", methods=['POST'])
def reservar():
    try:
        fecha = datetime.strptime(request.form['fecha'], '%Y-%m-%d').date()
        hora_entrada = datetime.strptime(request.form['hora_entrada'], '%H:%M').time()
        hora_salida = datetime.strptime(request.form['hora_salida'], '%H:%M').time()
        materia = request.form['materia'].strip()
        tutor = request.form['tutor'].strip()

        if not materia or not tutor:
            flash("Completar todos los campos", "error")
            return redirect(url_for('index'))

        if fecha < datetime.now().date():
            flash("La fecha debe ser hoy o posterior", "error")
            return redirect(url_for('index'))

        if hora_entrada <= hora_salida:#Validar el rango de horas
            flash("La hora de entrada debe ser anterior a la de salida", "error")
            return redirect(url_for('index'))

        existente = Reserva.query.filter_by(fecha=fecha, hora_entrada=hora_entrada).first()
        if existente:
            flash("Ya existe una reserva en ese día y horario", "error")
            return redirect(url_for('index'))

        nueva_reserva = Reserva(
            fecha=fecha,
            hora_entrada=hora_entrada,
            hora_salida=hora_salida,
            materia=materia,
            tutor=tutor
        )
        db.session.add(nueva_reserva)
        db.session.commit()
        flash("Reserva realizada con éxito", "success")
    except Exception as e:
        flash(f"Error al procesar la reserva: {str(e)}", "error")

    return redirect(url_for('index'))

@app.route("/eliminar-reserva/<int:id>", methods=["POST"])
def eliminar_reserva(id):
    reserva = Reserva.query.get(id)
    if reserva:
        db.session.delete(reserva)
        db.session.commit()
        flash("Reserva eliminada con éxito", "success")
    else:
        flash("Reserva no encontrada", "error")
    return redirect(url_for('index'))

def parse_hora(hora_str):
    try:
        return datetime.strptime(hora_str, '%H:%M:%S').time()
    except ValueError:
        return datetime.strptime(hora_str, '%H:%M').time()

@app.route('/actualizar/<int:id>', methods=['POST'])
def actualizar(id):
    reserva_actualizada = Reserva.query.get(id)
    if not reserva_actualizada:
        flash("Reserva no encontrada", "error")
        return redirect(url_for('index'))

    try:
        reserva_actualizada.fecha = datetime.strptime(request.form['fecha'], '%Y-%m-%d').date()
        reserva_actualizada.hora_entrada = parse_hora(request.form['hora_entrada'])
        reserva_actualizada.hora_salida = parse_hora(request.form['hora_salida'])
        reserva_actualizada.materia = request.form['materia'].strip()
        reserva_actualizada.tutor = request.form['tutor'].strip()

        if reserva_actualizada.hora_entrada >= reserva_actualizada.hora_salida:
            flash("La hora de entrada debe ser anterior a la de salida", "error")
            return redirect(url_for('index'))

        db.session.commit()
        flash("Reserva actualizada con éxito", "success")
    except Exception as e:
        flash(f"Error al actualizar la reserva: {str(e)}", "error")

    return redirect(url_for('index'))


# Main
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    print("Flask está corriendo en http://127.0.0.1:5000")
    app.run(debug=True)
