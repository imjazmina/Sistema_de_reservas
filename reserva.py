from flask import Flask, request, render_template, redirect, url_for  # type: ignore
from flask_sqlalchemy import SQLAlchemy  # type: ignore
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///reservas.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Modelo
class Reserva(db.Model):
    id = db.Column(db.Integer, primary_key=True)  
    fecha = db.Column(db.Date, nullable=False)
    hora_entrada = db.Column(db.Time, nullable=False)  
    hora_salida = db.Column(db.Time, nullable=False)
    nombre = db.Column(db.String(50), nullable=False)
    correo = db.Column(db.String(100), nullable=False)
    eliminar = db.column(db.booleano, default=False)

# Ruta principal
@app.route('/')
def index():
    return render_template('index.html')

# Ruta que guarda la reserva
@app.route('/reservar', methods=['POST'])  
def reservar():
    fecha = datetime.strptime(request.form['fecha'], '%Y-%m-%d').date()
    hora_entrada = datetime.strptime(request.form['hora_entrada'], '%H:%M').time()
    hora_salida = datetime.strptime(request.form['hora_salida'], '%H:%M').time()
    nombre = request.form['nombre']
    correo = request.form['correo']

    nueva_reserva = Reserva(
        fecha=fecha,
        hora_entrada=hora_entrada,
        hora_salida=hora_salida,
        nombre=nombre,
        correo=correo
    )
    db.session.add(nueva_reserva)
    db.session.commit()  
    return redirect(url_for('index')) 

@app.route("/eliminar-reserva/int:id>", methods =["POST"])
def eliminar_reserva():
    reserva= reserva.query.filter_by(id=id).firts()
    db.session.delete(reserva)
    db.session.commit()
    return redirect("/")
  


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
