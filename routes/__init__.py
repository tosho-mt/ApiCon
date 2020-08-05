""" rutas """
from functools import wraps
from flask import jsonify, request
from flaskext.mysql import MySQL 
import jwt
import json
from datetime import datetime
from uuid import uuid4 # genera una clave unica cada ves que lo ejecutas
from werkzeug.security import generate_password_hash, check_password_hash #encryptar
# from models import *
from app_core import app


# manejo de la base de @staticmethod
mysql = MySQL()
mysql.init_app(app)

# funciones DB
def consTablaPara(sql,parametros):
    data_json = []
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql,(parametros))
    header = [i[0] for i in cursor.description]
    data = cursor.fetchall()
    for i in data:
        data_json.append(dict(zip(header, i)))
    cursor.close()
    return data

def consTabla(sql):
    data_json = []    
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql)
    header = [i[0] for i in cursor.description]
    data = cursor.fetchall()    
    for i in data:
        data_json.append(dict(zip(header, i)))
    cursor.close()
    return data_json

def consInsTabla(sql,parametros):  
        # print(sql)
        # print(parametros) 
        data_json = [] 
        try:
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute(sql ,(parametros))
            conn.commit()
            data_json = {
                'mensage':'ok'
            }
            return data_json 
        except Exception as error:
            return jdata_json 

def consUpdTabla(sql,parametros):
        #print(parametros)
        #print(sql)
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(sql,(parametros))
        conn.commit()
        return 'ok'

# valida token
def valida_token(request):
    try:
        auth_header = request.headers.get('Authorization') # lee a cabecera
        # print(auth_header)
        if not auth_header or 'Bearer ' not in auth_header:
            return {'mensage':'encabezado de autorizacion incorrecto'}
        
        split = auth_header.split(' ')
        # print(split[1])
        
        if not len(split) == 2:
            return {'mensage':'encabezado de autorizacion incorrecto'}

        decode_data = jwt.decode(split[1], app.config['SECRET_KEY'])
        # print(decode_data)
        # import pdb; pdb.set_trace() ### para hacer debug
        user = consTablaPara("SELECT * FROM usuarios WHERE public_id=%s ",decode_data.get('user_id'))
        # user = User.query.filter_by(public_id=decode_data.get('user_id')).first()

        if not user:
            return {'mensage':'Usuario no existe'}
        return {'user':user[0][11]}

    except Exception as error:
        return {'mensage':'Error valida token.'}

def token_requerido(f):
    @wraps(f)
    def decorate(*args, **kwargs):
        res = valida_token(request)
        if not res.get('user'):
            return jsonify(res.get('mensage')), 401
        return f(res.get('user'), *args, **kwargs)
    return decorate

@app.route("/")
def root():
    return jsonify({'mensage':'inicio API'}) 


@app.route("/login", methods=['POST'])
def login():
    try:
        req = request.get_json(silent=True)

        if not req or not req.get('email') or not req.get('password'):
            return jsonify({
                'mensage':'No login data found.'
            })
        
        user = consTablaPara("SELECT * FROM usuarios WHERE email=%s ",req.get('email'))

        if user and check_password_hash(user[0][3],req.get('password').encode('utf-8')):
            token_data ={
                'user_id' : user[0][11],
                'IdUsu' : user[0][0],
                'Nombre' : user[0][1],
                'Email' : user[0][2],
                'TipoUsuario' : user[0][4],
                'CodCondominio' : user[0][7],
                'Celular' : user[0][8]
            }

            token = jwt.encode(token_data, app.config['SECRET_KEY'])
            return jsonify({'token':token.decode('UTF-8')})

        return jsonify({'mensage':'login invalido'}),401
    except Exception as error:
        return jsonify({'mensage':'Error al logearce' }),400

@app.route("/users")
@token_requerido
def get_users(current_user):
    data = consTabla ("SELECT * FROM usuarios ")
    return json.dumps(data)


@app.route("/user/<string:user_id>")
@token_requerido
def get_user(current_user,user_id):
    print(user_id)
    data = consTablaPara("SELECT * FROM usuarios WHERE public_id=%s ",user_id)
    return json.dumps(data)


@app.route("/user", methods=['POST'])
def create_user():
    req = request.get_json(silent=True)
    if not req:
        return jsonify({
            'mensage':'No json data found.'
        })
    try:
        nombre =  request.json['nombre']
        email = request.json['email']
        password = generate_password_hash( request.json['password'].encode('utf-8'),method="sha256")
        celular = request.json['celular']
        fecha = datetime.now().strftime("%Y%m%d")


        mensage = consInsTabla('INSERT INTO usuarios (Nombre, Email, Clave, TipoUsuario, Estado, fechaing, CodCondominio, celular,usuarioIng,UsuarioMod,public_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',[nombre,email,password,'1','Activo',fecha,0,celular,7,0,str(uuid4())])
        if mensage:
            user = consTablaPara("SELECT * FROM usuarios WHERE email=%s ",req.get('email'))
            token_data ={
                'user_id' : user[0][11],
                'IdUsu' : user[0][0],
                'Nombre' : user[0][1],
                'Email' : user[0][2],
                'TipoUsuario' : user[0][4],
                'CodCondominio' : user[0][7],
                'Celular' : user[0][8]
            }
        else:
             return jsonify({'mensage':'Usuario no creado.'})

        token = jwt.encode(token_data, app.config['SECRET_KEY'])
        return jsonify({'token':token.decode('UTF-8')})

        # return jsonify({
        #     'mensage':f'Creacion ok: {new_user.public_id}',
        #     'user':new_user.as_dict()
        # }) 
    except Exception as error:
        return jsonify({
            'mensage':'Error al crear usuario.'
        }),400

# @app.route("/user", methods=['POST'])
# def create_user():
#     req = request.get_json(silent=True)
#     if not req:
#         return jsonify({
#             'mensage':'No json data found.'
#         })
#     try:
#         email = request.json['email']
#         password = request.json['password']

#         new_user = User(email,password)

#         db.session.add(new_user)
#         db.session.commit()


#         return jsonify({
#             'mensage':f'Creacion ok: {new_user.public_id}',
#             'user':new_user.as_dict()
#         }) 
#     except Exception as error:
#         return jsonify({
#             'mensage':'Error al crear usuario.'
#         }),400

    