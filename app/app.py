from flask import Flask, jsonify, render_template, request, url_for, redirect
from flask_mysqldb import MySQL

app = Flask(__name__)

#Conexion a MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root' #usuario defecto de xamp
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'abaco'

conexcion = MySQL(app)


@app.before_request
def before_request():
    print("Antes de la peticion...")
    
@app.after_request
def after_request(responde):
    print("Despues de la petición")
    return responde


@app.route('/')
def index():
    cursos = ['PHP', 'Python', 'Java', 'Kotlin', 'Dart', 'JavaScript']
    data={
        'titulo':'Index',
        'bienvenida': 'Saludos!',
        'cursos':cursos,
        'numero_cursos' : len(cursos)
    }
    return render_template('index.html', data=data)

@app.route('/contacto/<nombre>/<int:edad>')
def contacto(nombre, edad):
    data={
        'titulo': 'Contacto',
        'nombre': nombre,
        'edad': edad
    }
    return render_template('contacto.html', data=data)


def query_string():
    print(request)
    print(request.args)
    print(request.args.get('param1'))
    print(request.args.get('param2'))
    return "Ok"

@app.route('/cursos_html')
def cursos_html():
    data={}
    try:
        orden = request.args.get('order', default='nombre')
        columnas_validas = ['codigo', 'nombre', 'creditos']
        
        #evitar inyecciones SQL asegurnado que solo se usen columnas válidas
        if orden not in columnas_validas:
            orden = 'nombre'
        
        cursor = conexcion.connection.cursor()
        sql=f"SELECT codigo, nombre, creditos FROM curso ORDER BY {orden} ASC"
        cursor.execute(sql)
        cursos = cursor.fetchall()
        return render_template('cursos.html', cursos=cursos, titulo='Listado de Cursos')
    except Exception as ex:
        print("ERROR:", str(ex))
        data['mensaje'] = 'Error...'
    return (data)
    
#Eliminar por su codigo
@app.route('/eliminar_curso/<int:codigo>', methods=['POST'])
def eliminar_curso(codigo):
    
    try:
        cursor = conexcion.connection.cursor()
        sql = "DELETE FROM curso WHERE codigo = %s"
        cursor.execute(sql,(codigo,))
        conexcion.connection.commit()
        return redirect(url_for('cursos_html'))
    except Exception as ex:
        print("ERROR:", str(ex))
        return render_template('error_html.html', error=str(ex))
#Actualizar valores
@app.route('/actualizar_curso/<int:codigo>', methods=['POST'])
def actualizar_curso(codigo):
    try:
        nombre = request.form['nombre']
        creditos = request.form['creditos']
        
        cursor = conexcion.connection.cursor()
        sql = "UPDATE curso SET nombre = %s, creditos = %s WHERE codigo = %s"
        cursor.execute(sql, (nombre, creditos, codigo))
        conexcion.connection.commit()
        
        return redirect(url_for('cursos_html'))
        
    except Exception as ex:
        print("ERROR:", ex)
        return render_template('error_html.html', error=str(ex))

@app.route('/cursos')
def listar_cursos():
    data={}
    try:
        cursor=conexcion.connection.cursor()
        sql="SELECT codigo, nombre, creditos FROM curso ORDER BY nombre ASC"
        cursor.execute(sql)
        cursos = cursor.fetchall()
        #print(cursos)
        data['cursos'] = cursos
        data['mensaje'] = 'Exito'
        
    except Exception as ex:
        data['mensaje'] = 'Error...'
        
    return jsonify(data)

def pagina_no_encontrada(error):
   # return render_template('404.html'), 404
   return redirect(url_for('index'))


if __name__ == '__main__':
    app.add_url_rule('/query_string', view_func=query_string)
    app.register_error_handler(404, pagina_no_encontrada)
    app.run(debug=True,port=5000)