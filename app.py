from flask_mail import Mail, Message
from flask import Flask, render_template, request, redirect
from werkzeug.utils import secure_filename
from bson import ObjectId
from pymongo import MongoClient
import os

def comprueba_fondo():
    pass

DOCUMENTOS = ["doc", "docx"]

def usuario():
    pass

def password():
    pass

EXTENSIONES = ["png", "jpg", "jpeg"]
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "./static/fondos"

app.config["MAIL_SERVER"] = "mail.cepibase.int"
app.config["MAIL_PORT"] = 25
app.config["MAIL_USERNAME"] = "DPereferrer"
app.config["MAIL_PASSWORD"] = "18561-01"
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = False
mail = Mail(app)

conexion = MongoClient("mongodb://localhost:27017")
basedatos = conexion.fondos_flask
colecc = basedatos.fondos
texto = "Hola "
fondoaenviarID = "ff"
destinatario = "dd"

def archivo_permitido(nombre):
    return "." in nombre and nombre.rsplit(".",1)[1] in EXTENSIONES

@app.route("/", methods=["GET", "POST"])
def abrir():
    activo=dict()
    activo["todos"] = "active"
    lista = colecc.find()
    return render_template('index.html', activo=activo, fondo="", lista=lista)

@app.route("/galeria", methods=['GET'])
def buscar():
    cat = request.values.get("tema")
    activo=dict()
    activo[cat] = "active"
    if cat is None:
        lista = colecc.find()
    else:
        lista = colecc.find({"categoria" : cat})
    return render_template('index.html', activo=activo, fondo="", lista=lista)

@app.route("/aportar")
def aportar():
    return render_template('aportar.html', mensaje="")

@app.route("/insertar", methods=["POST"])
def insertar():
    f = request.files['archivo']
    if f.filename == "":
        texto = "Hay que seleccionar un archivo"
    else:
        texto = "Nuevo fondo aportado."

        if archivo_permitido(f.filename):
            archivo = secure_filename(f.filename)
            f.save(os.path.join(app.config["UPLOAD_FOLDER"], archivo))
            texto = "Imagen cargada."
            imagen = archivo
            titulo = request.values.get("titulo")
            descripcion = request.values.get("descripcion")
            tags = []
            if request.values.get("animales"):
                tags.append("animales")
            if request.values.get("naturaleza"):
                tags.append("naturaleza")
            if request.values.get("ciudad"):
                tags.append("ciudad")                
            if request.values.get("deporte"):
                tags.append("deporte")
            if request.values.get("personas"):
                tags.append("personas")                            
            colecc.insert_one({"imagen":imagen, "titulo":titulo, "descripcion":descripcion, "categoria":tags})
        else:
            texto = "No se ha seleccionado un archivo de imagen."

    return render_template('aportar.html', mensaje=texto)

@app.route("/form_email", methods=["GET", "POST"])
def mail():
    global fondoaenviarID
  #  global destinatario
 #   destinatario = request.values.get("email")
    fondoID = request.values.get("_id")
  #  fondoaenviarID = fondoID
   # print(fondoID)
    fondo = colecc.find_one({"_id": ObjectId(fondoID)})
    fondoaenviarID = fondo["_id"]
    nombreFondo = fondo["imagen"]
  #  print(nombreFondo)
    return render_template('form_email.html', fondo=nombreFondo, titulo=fondo["titulo"], descripcion=fondo["descripcion"])

@app.route("/email", methods=["GET", "POST"])
def enviamail():
    global fondoaenviarID
    destinatario = request.values.get("email")
    mail = Mail(app)
  #  fondo = request
   #  fondoID = request.values.get("_id")
  #  print(fondoID)
    fondo = colecc.find_one({"_id": ObjectId(fondoaenviarID)})
  #  nombrefondo = fondo["imagen"]
    msg = Message(destinatario, sender = "alumno@cepibase.int")
    msg.recipients = [destinatario]
    msg.body = "aa"
    msg.html = render_template("email.html", titulo=fondo["titulo"], descripcion=fondo["descripcion"])
    with app.open_resource("./static/fondos/" + fondo["imagen"]) as adj: msg.attach(fondo["titulo"], "application/jpg", adj.read())
  #  with app.open_resource(fondo["imagen"]) as adj: msg.attach(fondo["titulo"], "application/jpg", adj.read())
    mail.send(msg)
   # return render_template('email.html', titulo=fondo["titulo"], descripcion=fondo["descripcion"])
   # return render_template('email.html', titulo=fondoaenviarID, descripcion="que tal")
    activo=dict()
    activo["todos"] = "active"
    lista = colecc.find()
    return render_template('index.html', activo=activo, fondo="", lista=lista)

if __name__ == "__main__":
    app.run()