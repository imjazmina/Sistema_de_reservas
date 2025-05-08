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

# Ruta principal: muestra reservas
@app.route('/')
def index():
    reservas = Reserva.query.order_by(Reserva.fecha).all()
    return render_template('index.html', reservas=reservas)

@app.route("/reservar", methods=['POST'])
def reservar():
    fecha = datetime.strptime(request.form['fecha'], '%Y-%m-%d').date()
    hora_entrada = datetime.strptime(request.form['hora_entrada'], '%H:%M').time()
    hora_salida = datetime.strptime(request.form['hora_salida'], '%H:%M').time()
    materia = request.form['materia']
    tutor = request.form['tutor']

    existente = Reserva.query.filter_by(fecha=fecha, hora_entrada=hora_entrada).first()
    
    if existente:
        flash("Ya hay una reserva en ese día y horario.")
    else:
        reserva = Reserva(
            fecha=fecha,
            hora_entrada=hora_entrada,
            hora_salida=hora_salida,
            materia=materia,
            tutor=tutor
        )
        db.session.add(reserva)
        db.session.commit()
        flash("Reserva realizada con éxito.")
    
    return redirect(url_for('index'))

# Ruta para eliminar una reserva
@app.route("/eliminar-reserva/<int:id>", methods=["POST"])
def eliminar_reserva(id):
    reserva = Reserva.query.filter_by(id=id).first()
    if reserva:
        db.session.delete(reserva)
        db.session.commit()
    return redirect(url_for('index'))

# Main
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    print("Flask está corriendo en http://127.0.0.1:5000")
    app.run(debug=True)