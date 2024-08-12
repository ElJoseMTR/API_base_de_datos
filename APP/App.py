from flask import Flask, request, jsonify, render_template
from flask_mysqldb import MySQL
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)
CORS(app)

# Configuración de la base de datos
app.config['MYSQL_HOST'] = 'bftrwaz6kfwo34lumlfh-mysql.services.clever-cloud.com'
app.config['MYSQL_USER'] = 'ut4todddupeqpt2a'
app.config['MYSQL_PASSWORD'] = '5wxAFBssL02f9aNstMV'
app.config['MYSQL_DB'] = 'bftrwaz6kfwo34lumlfh'
app.config['MYSQL_PORT'] = 21729
mysql = MySQL(app)

# Configuración de la clave secreta para Flask
app.secret_key = "mysecretkey"

# Nueva ruta para servir la página HTML de registro
@app.route('/')
def home():
    return render_template('register.html')
#pa ver todos los usuarios de la tabla de estudiantes
@app.route('/getuserAll', methods=['GET'])
def getAll():
    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM estudiantes')
        rv = cur.fetchall()
        cur.close()
        payload = []
        content = {}
        for result in rv:
            content = {'user': result[0], 'correo': result[1], 'password': result[2]}
            payload.append(content)
            content = {}
        return jsonify(payload)
    except Exception as e:
        print(e)
        return jsonify({"informacion": e})
    
@app.route('/testdb', methods=['GET'])
def test_db():
    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT VERSION()')
        version = cur.fetchone()
        cur.close()
        return jsonify({"version": version[0]})
    except Exception as e:
        return jsonify({"error": str(e)})


#para ver los cosas de un solo0 usuario de la tabla de estudiantes
@app.route('/getAllByUser/<user>', methods=['GET'])
def getAllByUser(user):
    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM estudiantes WHERE user = %s', (user,))
        rv = cur.fetchall()
        cur.close()
        payload = []
        for result in rv:
            content = {'user': result[0], 'correo': result[1], 'password': result[2]}
            payload.append(content)
        return jsonify(payload)
    except Exception as e:
        print(e)
        return jsonify({"informacion": str(e)})





@app.route('/checkPassword/<user>', methods=['POST'])
def check_password(user):
    try:
        data = request.json
        current_password = data.get('current_password')
        
        if not current_password:
            return jsonify({"informacion": "La contraseña actual es requerida"}), 400
        
        cur = mysql.connection.cursor()
        cur.execute('SELECT password FROM estudiantes WHERE user = %s', (user,))
        result = cur.fetchone()
        cur.close()
        
        if not result:
            return jsonify({"informacion": "Usuario no encontrado"}), 404
        
        stored_password_hash = result[0]
        
        if not check_password_hash(stored_password_hash, current_password):
            return jsonify({"informacion": "La contraseña actual es incorrecta"}), 401
        
        return jsonify({"mensaje": "La contraseña actual es correcta"})
    except Exception as e:
        print(e)
        return jsonify({"informacion": str(e)}), 500

@app.route('/updatePassword/<user>', methods=['PUT'])
def update_password(user):
    try:
        data = request.json
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')
        
        if new_password != confirm_password:
            return jsonify({"informacion": "Las contraseñas nuevas no coinciden"}), 400
        
        if not current_password or not new_password:
            return jsonify({"informacion": "La contraseña actual y la nueva contraseña son requeridas"}), 400
        
        cur = mysql.connection.cursor()
        cur.execute('SELECT password FROM estudiantes WHERE user = %s', (user,))
        result = cur.fetchone()
        cur.close()
        
        if not result:
            return jsonify({"informacion": "Usuario no encontrado"}), 404
        
        stored_password_hash = result[0]
        
        if not check_password_hash(stored_password_hash, current_password):
            return jsonify({"informacion": "La contraseña actual es incorrecta"}), 401
        
        new_password_hash = generate_password_hash(new_password)
        
        cur = mysql.connection.cursor()
        cur.execute('UPDATE estudiantes SET password = %s WHERE user = %s', (new_password_hash, user))
        mysql.connection.commit()
        cur.close()
        
        return jsonify({"mensaje": "Contraseña actualizada exitosamente"})
    except Exception as e:
        print(e)
        return jsonify({"informacion": str(e)}), 500

#para agregar un usuario en la tabla de estudiantes
@app.route('/add_user', methods=['POST'])
def add_contact():
    try:
        if request.method == 'POST':
            user = request.json['user']
            correo = request.json['correo']
            password = request.json['password']
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO estudiantes (user, correo, password) VALUES (%s, %s, %s)", (user, correo, password))
            mysql.connection.commit()
            return jsonify({"informacion": "Registro exitoso"})
    except Exception as e:
        print(e)
        return jsonify({"informacion": str(e)}), 400
    

#para ver todos los administradores tabla adminstrador
@app.route('/getadminAll', methods=['GET'])
def getadminAll():
    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM administrador')
        rv = cur.fetchall()
        cur.close()
        payload = []
        content = {}
        for result in rv:
            content = {'user': result[0]}
            payload.append(content)
            content = {}
        return jsonify(payload)
    except Exception as e:
        print(e)
        return jsonify({"informacion": e})
    
#para ver todos los mensajes que tiene un usuario
@app.route('/getmensajesadmin/<user>', methods=['GET'])
def getmensajesadmin(user):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM mensajesadmin WHERE user = %s", (user,))
        datos = cur.fetchall() 
        cur.close()
        if datos:
            return jsonify(datos)
        else:
            return jsonify({"error": "No tienes mensajes aun."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
#para obtener todos los mensajes de un administrador
@app.route('/getmensajesuserAdmin/<admin>', methods=['GET'])
def getmensajesuserAdmin(admin):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM mensajesadmin WHERE userAdmin = %s", (admin,))
        datos = cur.fetchall() 
        cur.close()
        
        if datos:
            return jsonify(datos)
        else:
            return jsonify({"error": "No tienes mensajes aun."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/getmensajesuserMedico/<medico>', methods=['GET'])
def getmensajesuserMedico(medico):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM mensajesmedico WHERE usermedico = %s", (medico,))
        datos = cur.fetchall() 
        cur.close()
        
        if datos:
            return jsonify(datos)
        else:
            return jsonify({"error": "No tienes mensajes aun."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
#para ver las respuestas que ha puesto un adminisitrador con el asunto
@app.route('/getrespuestasadmin/<asunto>', methods=['GET'])
def getrespuestasadmin(asunto):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT mensaje FROM respuestasadmin WHERE asunto = %s", (asunto,))
        datos = cur.fetchall()
        cur.close()
        
        if datos:
            return jsonify(datos)
        else:
            return jsonify({"error": "Aun no respondes a este mensaje"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
#para eliminar las respuestas de un asunto
@app.route('/deleterespuestas/<asunto>', methods=['DELETE'])
def deleterespuestas(asunto):
    try:
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM respuestasadmin WHERE asunto = %s', (asunto,))
        mysql.connection.commit()
        return jsonify({"informacion": "Registro eliminado"})
    except Exception as e:
        print(e)
        return jsonify({"informacion": str(e)})

#para eliminar los mensajes de un asunto
@app.route('/deletemensajes/<asunto>', methods=['DELETE'])
def deletemensajes(asunto):
    try:
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM mensajesadmin WHERE asunto = %s', (asunto,))
        mysql.connection.commit()
        return jsonify({"informacion": "Registro eliminado"})
    except Exception as e:
        print(e)
        return jsonify({"informacion": str(e)})
    
#para ver los mensajes de los medicos
@app.route('/getmensajesmedicos/<user>', methods=['GET'])
def getmensajesmedicos(user):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM mensajesmedico WHERE user = %s", (user,))
        datos = cur.fetchall()
        cur.close()
        
        if datos:
            return jsonify(datos)
        else:
            return jsonify({"error": "Aun no tienes mensajes"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#para ver las respuestas de un asunto
@app.route('/getrespuestasmedico/<asunto>', methods=['GET'])
def getrespuestasmedico(asunto):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT mensaje FROM respuestasmedico WHERE asunto = %s", (asunto,))
        datos = cur.fetchall()
        cur.close()
        
        if datos:
            return jsonify(datos)
        else:
            return jsonify({"error": "Aun no hay respuesta. Revisa mas tarde"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#para eliminar las respuestas de un medico con el asunto
@app.route('/deleterespuestasmedico/<asunto>', methods=['DELETE'])
def deleterespuestasmedico(asunto):
    try:
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM respuestasmedico WHERE asunto = %s', (asunto,))
        mysql.connection.commit()
        return jsonify({"informacion": "Registro eliminado"})
    except Exception as e:
        print(e)
        return jsonify({"informacion": str(e)})
    
#para eliminar los mensajes de un medico
@app.route('/deletemensajesmedico/<asunto>', methods=['DELETE'])
def deletemensajesmedico(asunto):
    try:
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM mensajesmedico WHERE asunto = %s', (asunto,))
        mysql.connection.commit()
        return jsonify({"informacion": "Registro eliminado"})
    except Exception as e:
        print(e)
        return jsonify({"informacion": str(e)})
    
#para ver todos los medicos
@app.route('/getmedicosAll', methods=['GET'])
def getmedicosAll():
    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM medico')
        rv = cur.fetchall()
        cur.close()
        payload = []
        content = {}
        for result in rv:
            content = {'user': result[0]}
            payload.append(content)
            content = {}
        return jsonify(payload)
    except Exception as e:
        print(e)
        return jsonify({"informacion": e})
    
#para agregar un mensaje de los administrador
@app.route('/add_mensaje_admin', methods=['POST'])
def add_mensaje_admin():
    try:
        if request.method == 'POST':
            data = request.json
            user = data['user']
            userAdmin = data['userAdmin']
            mensaje = data['mensaje']
            asunto = data['asunto']
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO mensajesadmin (user, userAdmin, mensaje, asunto) VALUES (%s, %s, %s, %s)", (user, userAdmin, mensaje, asunto))
            mysql.connection.commit()
            return jsonify({"informacion": "Registro exitoso"})
    except Exception as e:
        print(e)
        return jsonify({"informacion": str(e)}), 400
    
#para egreagr un mensahe medico
@app.route('/add_mensaje_medico', methods=['POST'])
def add_mensaje_medico():
    try:
        if request.method == 'POST':
            data = request.json
            user = data['user']
            usermedico = data['usermedico']
            mensaje = data['mensaje']
            asunto = data['asunto']
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO mensajesmedico (user, usermedico, mensaje, asunto) VALUES (%s, %s, %s, %s)", (user, usermedico, mensaje, asunto))
            mysql.connection.commit()
            return jsonify({"informacion": "Registro exitoso"})
    except Exception as e:
        print(e)
        return jsonify({"informacion": str(e)}), 400

#para actualizar un administrador
@app.route('/updateuser/<user>', methods=['PUT'])
def update_contact(user):
    try:
        correo = request.json['correo']
        password = request.json['password']
        cur = mysql.connection.cursor()
        cur.execute("""
        UPDATE estudiantes
        SET correo = %s,
            password = %s
        WHERE user = %s
        """, (correo, password, user))
        mysql.connection.commit()
        return jsonify({"informacion": "Registro actualizado"})
    except Exception as e:
        print(e)
        return jsonify({"informacion": str(e)})

#para que el administrador pueda agregar una respuestas a
@app.route('/add_respuesta_admin', methods=['POST'])
def add_respuesta_admin():
    try:
        if request.method == 'POST':
            data = request.json
            user = data['user']
            usersdmin = data['usersdmin']
            mensaje = data['mensaje']
            asunto = data['asunto']
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO respuestasadmin (useradmin, user, asunto, mensaje) VALUES (%s, %s, %s, %s)", (usersdmin, user, asunto, mensaje))
            mysql.connection.commit()
            return jsonify({"informacion": "Registro exitoso"})
    except Exception as e:
        print(e)
        return jsonify({"informacion": str(e)}), 400
    
@app.route('/add_respuesta_medico', methods=['POST'])
def add_respuesta_medico():
    try:
        if request.method == 'POST':
            data = request.json
            user = data['user']
            usermedico = data['usermedico']
            mensaje = data['mensaje']
            asunto = data['asunto']
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO respuestasmedico (usermedico, user, asunto, mensaje) VALUES (%s, %s, %s, %s)", (usermedico, user, asunto, mensaje))
            mysql.connection.commit()
            return jsonify({"informacion": "Registro exitoso"})
    except Exception as e:
        print(e)
        return jsonify({"informacion": str(e)}), 400

#para eliminar un estudiantge
@app.route('/delete/<user>', methods=['DELETE'])
def delete_contact(user):
    try:
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM estudiantes WHERE user = %s', (user,))
        mysql.connection.commit()
        return jsonify({"informacion": "Registro eliminado"})
    except Exception as e:
        print(e)
        return jsonify({"informacion": str(e)})
    
#para el login de la pag
@app.route('/login', methods=['GET'])
def login():
    try:
        user = request.args.get('user')
        password = request.args.get('password')
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM estudiantes WHERE user = %s AND password = %s', (user, password))
        rv = cur.fetchone()
        cur.close()
        if rv:
            return jsonify({"informacion": "Inicio de sesión exitoso"})
        else:
            return jsonify({"informacion": "Credenciales incorrectas"})
    except Exception as e:
        print(e)
        return jsonify({"informacion": str(e)}), 400
    
#para el login del admin
@app.route('/loginAdmin', methods=['GET'])
def loginAdmin():
    try:
        user = request.args.get('user')
        password = request.args.get('password')
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM administrador WHERE user = %s AND password = %s', (user, password))
        rv = cur.fetchone()
        cur.close()
        if rv:
            return jsonify({"informacion": "Inicio de sesión exitosoo"})
        else:
            return jsonify({"informacion": "Credenciales incorrectas"})
    except Exception as e:
        print(e)
        return jsonify({"informacion": str(e)}), 400
    
@app.route('/loginMedico', methods=['GET'])
def loginMedico():
    try:
        user = request.args.get('user')
        password = request.args.get('password')
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM medico WHERE user = %s AND password = %s', (user, password))
        rv = cur.fetchone()
        cur.close()
        if rv:
            return jsonify({"informacion": "Inicio de sesión exitosoo"})
        else:
            return jsonify({"informacion": "Credenciales incorrectas"})
    except Exception as e:
        print(e)
        return jsonify({"informacion": str(e)}), 400



#para agregar datos de los estudiantes
@app.route('/add_datos', methods=['POST'])
def add_datos():
    try:
        if request.method == 'POST':
            user = request.json['user']
            nombre = request.json['nombre']
            apellido = request.json['apellido']
            edad = request.json['edad']
            carrera = request.json['carrera']
            cuatrimestre = request.json['cuatrimestre']
            deporte = request.json['deporte']
            genero = request.json['genero']
            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO datos (user, nombre, apellido, edad, carrera, cuatrimestre, deporte, genero) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (user, nombre, apellido, edad, carrera, cuatrimestre, deporte, genero))
            mysql.connection.commit()
            return jsonify({"informacion": "Registro exitoso"})
    except Exception as e:
        print(e)
        return jsonify({"informacion": str(e)}), 400
    


#para ver si que estudiantes tienen datos estudiantes
@app.route('/obtener_usuario', methods=['GET'])
def obtener_usuariosuser():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM datos")
        datos = cur.fetchall()
        cur.close()
        return jsonify(datos)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
#para  obetener las datos de un estudiante especifico
@app.route('/obtener_usuariouser/<user>', methods=['GET'])
def obtener_usuario_por_user(user):
    try:
        conn = mysql.connect
        cursor = conn.cursor()
        cursor.execute("SELECT user, nombre, apellido, edad, carrera, cuatrimestre, deporte, genero FROM datos WHERE user = %s", (user,))
        data = cursor.fetchone()
        cursor.close()
        conn.close()

        if data:
            usuario = {
                'user': data[0],
                'nombre': data[1],
                'apellido': data[2],
                'edad': data[3],
                'carrera': data[4],
                'cuatrimestre': data[5],
                'deporte': data[6],
                'genero': data[7]
            }
            return jsonify(usuario)
        else:
            return jsonify({'error': 'El usuario no tiene datos'}), 404

    except Exception as e:
        app.logger.error(f"Error al obtener usuario: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500
    
@app.route('/obtener_datosmedico/<user>', methods=['GET'])
def obtener_datosmedico(user):
    try:
        conn = mysql.connect
        cursor = conn.cursor()
        cursor.execute("SELECT user, frecuencia_ejercicio, tiempo_ejercicio, comer_frutas, comer_comida_chatarra, tiempo_dormir, fumas, alcohol, frecuencia_medico, enfermedades FROM preguntas WHERE user = %s", (user,))
        data = cursor.fetchone()
        cursor.close()
        conn.close()

        if data:
            usuario = {
                'user': data[0],
                'frecuencia_ejercicio': data[1],
                'tiempo_ejercicio': data[2],
                'comer_frutas': data[3],
                'comer_comida_chatarra': data[4],
                'tiempo_dormir': data[5],
                'fumas': data[6],
                'alcohol': data[7],
                'frecuencia_medico': data[8],
                'enfermedades': data[9]
            }
            return jsonify(usuario)
        else:
            return jsonify({'error': 'El usuario no tiene datos'}), 404

    except Exception as e:
        app.logger.error(f"Error al obtener usuario: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500



#para ver los datos de los administradores
@app.route('/getAllByDatosadmin/<user>', methods=['GET'])
def getAllByDatosadmin(user):
    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM datos_admin WHERE user = %s', (user,))
        rv = cur.fetchall()
        cur.close()
        
        payload = []
        for result in rv:
            content = {
                'user': result[0], 
                'nombre': result[1], 
                'apellido': result[2], 
                'edad': result[3], 
                'CC': result[4]
            }
            payload.append(content)
            
        if rv:
            return jsonify({"informacion": "Ya tiene formulario registrado"})
        else:
            return jsonify({"informacion": "Haga el Formulario"})
    except Exception as e:
        print(e)
        return jsonify({"informacion": str(e)})
    
#para ver los datos de un medico
@app.route('/getAllByDatosmedico/<user>', methods=['GET'])
def getAllByDatosmedico(user):
    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM datos_medico WHERE user = %s', (user,))
        rv = cur.fetchall()
        cur.close()
        
        payload = []
        for result in rv:
            content = {
                'user': result[0], 
                'nombre': result[1], 
                'apellido': result[2], 
                'edad': result[3], 
                'CC': result[4]
            }
            payload.append(content)
            
        if rv:
            return jsonify({"informacion": "Ya tiene formulario registrado"})
        else:
            return jsonify({"informacion": "Haga el Formulario"})
    except Exception as e:
        print(e)
        return jsonify({"informacion": str(e)})


#para actualizar los datos de los estudiantes
@app.route('/updatedatos/<user>', methods=['PUT'])
def updatedatos(user):
    try:
        nombre = request.json['nombre']
        apellido = request.json['apellido']
        edad = request.json['edad']
        carrera = request.json['carrera']
        cuatrimestre = request.json['cuatrimestre']
        deporte = request.json['deporte']
        genero = request.json['genero']
        
        cur = mysql.connection.cursor()
        cur.execute("""
        UPDATE datos
        SET nombre = %s,
            apellido = %s,
            edad = %s,
            carrera = %s,
            cuatrimestre = %s,
            deporte = %s,
            genero = %s
        WHERE user = %s
        """, (nombre, apellido, edad, carrera, cuatrimestre, deporte, genero, user))  # Aquí se añade el 'user'
        
        mysql.connection.commit()
        return jsonify({"informacion": "Registro actualizado"})
    except Exception as e:
        print(e)
        return jsonify({"informacion": str(e)})


#para eliminar datos de estudiantes
@app.route('/deletedatos/<user>', methods=['DELETE'])
def deletedatos(user):
    try:
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM datos WHERE user = %s', (user,))
        mysql.connection.commit()
        return jsonify({"informacion": "Registro eliminado"})
    except Exception as e:
        print(e)
        return jsonify({"informacion": str(e)})

#para ver si un admin ya hjio el formulario
@app.route('/formulario_admin', methods=['POST'])
def formulario_admin():
    try:
        if request.method == 'POST':
            data = request.json
            print("Datos recibidos:", data)  # Para depuración

            user = data['user']
            nombre = data['nombre']
            apellido = data['apellido']
            edad = data['edad']
            cc = data['CC']

            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO datos_admin (user, nombre, apellido, edad, CC) VALUES (%s, %s, %s, %s, %s)", 
                        (user, nombre, apellido, edad, cc))
            mysql.connection.commit()
            cur.close()
            return jsonify({"informacion": "Registro exitoso"})
    except Exception as e:
        print(e)
        return jsonify({"informacion": str(e)}), 400
    
@app.route('/formulario_medico', methods=['POST'])
def formulario_medico():
    try:
        if request.method == 'POST':
            data = request.json
            print("Datos recibidos:", data)  # Para depuración

            user = data['user']
            nombre = data['nombre']
            apellido = data['apellido']
            edad = data['edad']
            cc = data['CC']

            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO datos_medico (user, nombre, apellido, edad, CC) VALUES (%s, %s, %s, %s, %s)", 
                        (user, nombre, apellido, edad, cc))
            mysql.connection.commit()
            cur.close()
            return jsonify({"informacion": "Registro exitoso"})
    except Exception as e:
        print(e)
        return jsonify({"informacion": str(e)}), 400

#para agregar un form,ualrio / datos
@app.route('/formulario_user', methods=['POST'])
def formulario_user():
    try:
        if request.method == 'POST':
            data = request.json
            print("Datos recibidos:", data)  

            user = data['user']
            nombre = data['nombre']
            apellido = data['apellido']
            edad = data['edad']
            carrera = data['carrera']
            cuatrimestre = data['cuatrimestre']
            deporte = data['deporte']
            genero = data['genero']

            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO datos (user, nombre, apellido, edad, carrera, cuatrimestre, deporte, genero) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", 
                        (user, nombre, apellido, edad, carrera, cuatrimestre, deporte, genero))
            mysql.connection.commit()
            cur.close()
            return jsonify({"informacion": "Registro exitoso"})
    except Exception as e:
        print(e)
        return jsonify({"informacion": str(e)}), 400
    
#para agregar las poresopestasn a reguntas
@app.route('/setPreguntasUser', methods=['POST'])
def setPreguntasUser():
    try:
        if request.method == 'POST':
            data = request.json
            print("Datos recibidos:", data)  
            
            user = data['user']
            frecuencia_ejercicio = data['frecuencia_ejercicio']
            tiempo_ejercicio = data['tiempo_ejercicio']
            comer_frutas = data['comer_frutas']
            comer_comida_chatarra = data['comer_comida_chatarra']
            tiempo_dormir = data['tiempo_dormir']
            fumas = data['fumas']
            alcohol = data['alcohol']
            frecuencia_medico = data['frecuencia_medico']
            enfermedades = data['enfermedades']

            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO preguntas (user, frecuencia_ejercicio, tiempo_ejercicio, comer_frutas, comer_comida_chatarra, tiempo_dormir, fumas, alcohol, frecuencia_medico, enfermedades) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                        (user, frecuencia_ejercicio, tiempo_ejercicio, comer_frutas, comer_comida_chatarra, tiempo_dormir, fumas, alcohol, frecuencia_medico, enfermedades))
            mysql.connection.commit()
            cur.close()
            return jsonify({"informacion": "Registro exitoso"})
    except Exception as e:
        print(e)
        return jsonify({"informacion": str(e)}), 400

#agregar diagnostico 
@app.route('/setdiagnostico', methods=['POST'])
def setdiagnostico():
    try:
        if request.method == 'POST':
            data = request.json
            print("Datos recibidos:", data)  
            
            user = data['user']
            text_diagnostico = data['text_diagnostico']

            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO diagnostico (user, text_diagnostico) VALUES (%s, %s)", 
                        (user, text_diagnostico))
            mysql.connection.commit()
            cur.close()
            return jsonify({"informacion": "Registro exitoso"})
    except Exception as e:
        print(e)
        return jsonify({"informacion": str(e)}), 400
#coger el diagnostico de un usuarop0
@app.route('/getdiagnostico/<user>', methods=['GET'])
def getdiagnostico(user):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT text_diagnostico FROM diagnostico WHERE user = %s", (user,))
        result = cur.fetchone()
        cur.close()
        
        if result:
            return jsonify({"informacion": result[0]})
        else:
            return jsonify({"informacion": "El usuario aun no tiene diagnostico"}), 404
    except Exception as e:
        print(e)
        return jsonify({"informacion": str(e)}), 400
#pillar las recomendaciones de un usuario
@app.route('/getrecomendaciones/<user>', methods=['GET'])
def getrecomendaciones(user):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT text_recomendaciones FROM recomendaciones WHERE user = %s", (user,))
        result = cur.fetchone()
        cur.close()
        
        if result:
            return jsonify({"informacion": result[0]})
        else:
            return jsonify({"informacion": "El usuario aun no tiene recomendaciones"}), 404
    except Exception as e:
        print(e)
        return jsonify({"informacion": str(e)}), 400

    
    #agregar recomendaciones
@app.route('/setrecomendaciones', methods=['POST'])
def setrecomendaciones():
    try:
        if request.method == 'POST':
            data = request.json
            print("Datos recibidos:", data)  
            
            user = data['user']
            text_recomendaciones = data['text_recomendaciones']

            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO recomendaciones (user, text_recomendaciones) VALUES (%s, %s)", 
                        (user, text_recomendaciones))
            mysql.connection.commit()
            cur.close()
            return jsonify({"informacion": "Registro exitoso"})
    except Exception as e:
        print(e)
        return jsonify({"informacion": str(e)}), 400

#para ver todos los dartos de 8un estudiantge
@app.route('/getAllByDatos/<user>', methods=['GET'])
def getAllByDatos(user):
    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM datos WHERE user = %s', (user,))
        rv = cur.fetchall()
        cur.close()
        
        payload = []
        for result in rv:
            content = {
                'user': result[0], 
                'nombre': result[1], 
                'apellido': result[2], 
                'edad': result[3], 
                'carrera': result[4], 
                'cuatrimestre': result[5], 
                'deporte': result[6], 
                'genero': result[7]
            }
            payload.append(content)
            
        if rv:
            return jsonify({"informacion": "Ya tiene formulario registrado"})
        else:
            return jsonify({"informacion": "Haga el Formulario"})
    except Exception as e:
        print(e)
        return jsonify({"informacion": str(e)})
    
#para ver todos los datos de laos estudiantes
@app.route('/getAllDatos', methods=['GET'])
def getAllDatos():
    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM datos')
        rv = cur.fetchall()
        cur.close()
        payload = []
        content = {}
        for result in rv:
            content = {'user': result[0],
                'nombre': result[1],
                'apellido': result[2],
                'edad': result[3],
                'carrera': result[4],
                'cuatrimestre': result[5],
                'deporte': result[6],
                'genero': result[7]}
            payload.append(content)
            content = {}
        return jsonify(payload)
    except Exception as e:
        print(e)
        return jsonify({"informacion": e})

#meyores de edad
@app.route('/usuarios_mayores_de_edad', methods=['GET'])
def usuarios_mayores_de_edad():
    try:
        cur = mysql.connection.cursor()
        
        cur.execute("""
            SELECT 
                CASE WHEN edad >= 18 THEN 'mayores_de_18' ELSE 'menores_de_18' END as grupo,
                COUNT(*) as total
            FROM datos
            GROUP BY grupo
        """)
        rv = cur.fetchall()
        cur.close()
        
       
        mayores_de_18 = 0
        menores_de_18 = 0

       
        for result in rv:
            if result[0] == 'mayores_de_18':
                mayores_de_18 = result[1]
            elif result[0] == 'menores_de_18':
                menores_de_18 = result[1]

        payload = {
            'mayores_de_18': mayores_de_18,
            'menores_de_18': menores_de_18
        }

        return jsonify(payload)
    except Exception as e:
        print(e)
        return jsonify({"informacion": str(e)})
#usuarios fumas
@app.route('/usuarios_fuman', methods=['GET'])
def usuarios_fuman():
    try:
        cur = mysql.connection.cursor()
        
        cur.execute("""
            SELECT 
                fumas as grupo,
                COUNT(*) as total
            FROM preguntas
            GROUP BY fumas
        """)
        rv = cur.fetchall()
        cur.close()
        
        fuman = 0
        no_fuman = 0

        # Agrupar los resultados
        for result in rv:
            if result[0] == 'Sí':
                fuman = result[1]
            elif result[0] == 'No':
                no_fuman = result[1]

        payload = {
            'fuman': fuman,
            'no_fuman': no_fuman
        }

        return jsonify(payload)
    except Exception as e:
        print(e)
        return jsonify({"informacion": str(e)})

# toman alcohol
@app.route('/usuarios_alcohol', methods=['GET'])
def usuarios_alcohol():
    try:
        cur = mysql.connection.cursor()
        
        cur.execute("""
            SELECT 
                alcohol as grupo,
                COUNT(*) as total
            FROM preguntas
            GROUP BY alcohol
        """)
        rv = cur.fetchall()
        cur.close()
        
        toman_alcohol = 0
        no_toman_alcohol = 0

        # Agrupar los resultados
        for result in rv:
            if result[0] == 'Sí':
                toman_alcohol = result[1]
            elif result[0] == 'No':
                no_toman_alcohol = result[1]

        payload = {
            'toman_alcohol': toman_alcohol,
            'no_toman_alcohol': no_toman_alcohol
        }

        return jsonify(payload)
    except Exception as e:
        print(e)
        return jsonify({"informacion": str(e)})

#cont6eo de usuarios por carreras
@app.route('/usuarios_por_carrera', methods=['GET'])
def usuarios_por_carrera():
    try:
        cur = mysql.connection.cursor()
        
        cur.execute("""
            SELECT carrera, COUNT(*) as total
            FROM datos
            WHERE carrera IN (
                'Ingeniería Eléctrica',
                'Ingeniería en Seguridad y Salud en el Trabajo',
                'Ingeniería Industrial',
                'Ingeniería Mecatrónica',
                'Ingeniería Telemática',
                'Diseño Gráfico',
                'Administración de Negocios Internacionales',
                'Licenciatura en Educación Básica Primaria'
            )
            GROUP BY carrera
        """)
        rv = cur.fetchall()
        cur.close()
        

        carreras = {
            'Ingeniería Eléctrica': 0,
            'Ingeniería en Seguridad y Salud en el Trabajo': 0,
            'Ingeniería Industrial': 0,
            'Ingeniería Mecatrónica': 0,
            'Ingeniería Telemática': 0,
            'Diseño Gráfico': 0,
            'Administración de Negocios Internacionales': 0,
            'Licenciatura en Educación Básica Primaria': 0
        }

      
        for result in rv:
            carrera = result[0]
            total = result[1]
            if carrera in carreras:
                carreras[carrera] = total

        return jsonify(carreras)
    except Exception as e:
        print(e)
        return jsonify({"informacion": str(e)})

#genero estadisticas
@app.route('/usuarios_por_genero', methods=['GET'])
def usuarios_por_genero():
    try:
        cur = mysql.connection.cursor()
        
       
        cur.execute("""
            SELECT genero, COUNT(*) as total
            FROM datos
            WHERE genero IN ('masculino', 'femenino')
            GROUP BY genero
        """)
        rv = cur.fetchall()
        cur.close()
        
        generos = {
            'masculino': 0,
            'femenino': 0
        }

        for result in rv:
            genero = result[0]
            total = result[1]
            if genero in generos:
                generos[genero] = total

        return jsonify(generos)
    except Exception as e:
        print(e)
        return jsonify({"informacion": str(e)})

    
#para ver las respuestas a las preguntasm de un estusiante
@app.route('/getAllPreguntas/<user>', methods=['GET'])
def getAllPreguntas(user):
    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM preguntas WHERE user = %s', (user,))
        rv = cur.fetchall()
        cur.close()
        
        payload = []
        for result in rv:
            content = {
                'user': result[0], 
                'frecuencia_ejercicio': result[1], 
                'tiempo_ejercicio': result[2], 
                'comer_frutas': result[3], 
                'comer_comida_chatarra': result[4], 
                'tiempo_dormir': result[5], 
                'fumas': result[6], 
                'alcohol': result[7],
                'frecuencia_medico': result[8],
                'enfermedades': result[9]
            }
            payload.append(content)
            
        if rv:
            return jsonify({"informacion": "Ya tiene preguntas registrado"})
        else:
            return jsonify({"informacion": "Haga las preguntas"})
    except Exception as e:
        print(e)
        return jsonify({"informacion": str(e)})

#ver los datos de las preguntas
@app.route('/verrespuestas_a_preguntas/<user>', methods=['GET'])    
def verrespuestas_a_preguntas(user):
    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM preguntas WHERE user = %s', (user,))
        rv = cur.fetchall()
        cur.close()

        if rv:
            payload = []
            for result in rv:
                content = {
                    'user': result[0], 
                    'frecuencia_ejercicio': result[1], 
                    'tiempo_ejercicio': result[2], 
                    'comer_frutas': result[3], 
                    'comer_comida_chatarra': result[4], 
                    'tiempo_dormir': result[5], 
                    'fumas': result[6], 
                    'alcohol': result[7],
                    'frecuencia_medico': result[8],
                    'enfermedades': result[9]
                }
                payload.append(content)
            return jsonify(payload)
        else:
            return jsonify({"informacion": "El usuario aun no ha respondido las preguntas"})
    except Exception as e:
        print(e)
        return jsonify({"informacion": str(e)})



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000, debug=True)


