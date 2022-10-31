

from datetime import datetime
import os
from flask import Flask
from flask import render_template,request,redirect,url_for, flash
from flaskext.mysql import MySQL
from flask import send_from_directory


app = Flask(__name__)
app.secret_key="Develoteca"

mysql = MySQL()#declarar el mysql
app.config['MYSQL_DATABASE_HOST'] = 'localhost'#el nombre del host, el nombre d ela variable tiene que estar en mayuscula
app.config['MYSQL_DATABASE_USER'] = 'root'#el usuario
app.config['MYSQL_DATABASE_PASSWORD'] = ''#la contraseña
app.config['MYSQL_DATABASE_DB'] = 'sistema'#el nombre de la base de datos
mysql.init_app(app)#crear la conexion con esos datoss

CARPETA = os.path.join('uploads')
app.config['CARPETA']= CARPETA

@app.route('/uploads/<nombreFoto>')
def uploads(nombreFoto):
    return send_from_directory(app.config['CARPETA'],nombreFoto)

@app.route('/')
def index():

    sql = "SELECT * FROM `empleados`;"
    conn= mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql)

    empleados= cursor.fetchall()
    print(empleados)

    conn.commit()
    return render_template('empleados/index.html', empleados=empleados )

#ir a la pestaña create.html
@app.route('/create')
def create():
    return render_template('empleados/create.html')

#crear
@app.route('/store', methods=['POST'])
def storage():
    _nombre = request.form['txtNombre']
    _correo = request.form['txtCorreo']
    _foto = request.files['txtFoto']

    #validacion
    if _nombre=='' or _correo =='' or _foto=='':
        flash('Tienes que llenar todos los campos')
        return redirect(url_for('create'))

    now= datetime.now() #now va a almacenar todo lo que es el tiempo actualmente
    tiempo = now.strftime("%Y%M%H%S")#fotmato de año,mes,hora,segundos

    if _foto.filename!='':#sino esa foto no esta vacio, lo que va hacer es obtener el nombre del tiempo y concatenarlo a la foto, con el fin de no sobrescribir la foto anterior
        nuevoNombreFoto= tiempo + _foto.filename
        _foto.save("uploads/"+nuevoNombreFoto)#vamos a guardar esa foto, y lo vamoa a subir a la carpeta uploads

    sql = "INSERT INTO `empleados` (`id`, `nombre`, `email`, `foto`) VALUES (NULL, %s, %s, %s);"

    datos = (_nombre,_correo,nuevoNombreFoto)
    conn= mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql,datos)
    conn.commit()
    return redirect('/')


#Modificar
@app.route('/update', methods=['POST'])
def update():
    _nombre = request.form['txtNombre']
    _correo = request.form['txtCorreo']
    _foto = request.files['txtFoto']
    id=request.form['txtID']

    sql = "UPDATE `empleados` SET `nombre`=%s, `email`=%s WHERE `id`=%s ;"

    datos = (_nombre,_correo,id)
    conn = mysql.connect()
    cursor = conn.cursor()

    now = datetime.now() 
    tiempo = now.strftime("%Y%m%H%S")

    if _foto.filename != '':
        nuevoNombreFoto = tiempo+_foto.filename
        _foto.save("uploads/"+nuevoNombreFoto)
        cursor.execute("SELECT foto FROM empleados WHERE id=%s", id)
        fila = cursor.fetchall()

        os.remove(os.path.join(app.config['CARPETA'],fila[0][0]))
        cursor.execute("UPDATE empleados SET foto=%s WHERE id=%s",(nuevoNombreFoto,id))
        conn.commit()

    cursor.execute(sql,datos)
    conn.commit()
    return redirect('/')
#borrar
@app.route('/destroy/<int:id>')
def destroy(id):
    conn= mysql.connect()
    cursor=conn.cursor()

    cursor.execute("SELECT foto FROM empleados WHERE id=%s", id)
    fila=cursor.fetchall()
    os.remove(os.path.join(app.config['CARPETA'],fila[0][0]))

    cursor.execute("DELETE FROM empleados WHERE id=%s",(id))
    conn.commit()
    return redirect('/')

#verlos datos que se van a editar en la pestaña edit.html
@app.route('/edit/<int:id>')
def edit(id):
    conn= mysql.connect()
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM empleados WHERE id=%s", (id))
    empleados=cursor.fetchall()
    conn.commit()
    #print(empleados)
    return render_template('empleados/edit.html', empleados=empleados)




if __name__ == '__main__':
    app.run(debug=True)


# para ejecutar el python es  flask run

