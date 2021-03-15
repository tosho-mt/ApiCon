""" rutas """
from functools import wraps
from flask import jsonify, request
import requests
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

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql,(parametros))
    data = cursor.fetchall()
    cursor.close()
    return data

def consTablaParaL(sql,parametros):
    # print(sql)
    # print(parametros)
    data_json = []
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql,(parametros))
    header = [i[0] for i in cursor.description]
    data = cursor.fetchall()
    for i in data:
        data_json.append(dict(zip(header, i)))
    cursor.close()
    return data_json

def consTabla(sql):
    # print(sql)
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
            return data_json 

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
        
        return {'user':user[0][11],'id':user[0][0]}

    except Exception as error:
        return {'mensage':'Error valida token.'}

def token_requerido(f):
    @wraps(f)
    def decorate(*args, **kwargs):

        res = valida_token(request)
        if not res.get('id'):
            return jsonify(res.get('mensage')), 401
        return f(res.get('id'), *args, **kwargs)
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

        param = req.get('password').split(" --- ")
        if user and check_password_hash(user[0][3],param[0].encode('utf-8')):
            token_data ={
                'user_id' : user[0][11],
                'IdUsu' : user[0][0],
                'Nombre' : user[0][1],
                'Email' : user[0][2],
                'TipoUsuario' : user[0][4],
                'CodCondominio' : user[0][7],
                'Celular' : user[0][8],
                'codPersona' : user[0][12]
            }

            token = jwt.encode(token_data, app.config['SECRET_KEY'])

            ## crear relacion fcm y usuarios
            fecha = datetime.now().strftime("%Y%m%d")

            contacto = consTablaPara("SELECT * FROM contactos WHERE idPersona=%s and Tipo = 7 and valor=%s",[user[0][12],param[1].encode('utf-8')])
            if not contacto:
                consInsTabla('INSERT INTO fcmusuarios (codusuario, codfcm, estado,fechaing) VALUES (%s,%s,%s,%s)',[user[0][12],param[1].encode('utf-8'),'Activo',fecha])
                consInsTabla('INSERT INTO contactos (idPersona, Tipo, valor, estado, fechaIng, token) VALUES (%s,%s,%s,%s,%s,%s)',[user[0][12],7,param[1].encode('utf-8'),'Activo',fecha,""])#fcm tipo contacto

            return jsonify({'token':token.decode('UTF-8')})

        return jsonify({'mensage':'login invalido'}),401
    except Exception as error:
        return jsonify({'mensage':'Error al logearce' }),400

@app.route("/users")
@token_requerido
def get_users(current_user):
    # print(current_user)

    data = consTabla ("SELECT * FROM usuarios ")
    return json.dumps(data)


@app.route("/user/<string:user_id>")
@token_requerido
def get_user(current_user,user_id):
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
        codpersona = request.json['codpersona']
        cedula=  request.json['cedula']
        apellido =   request.json['apellido']
        fechanacimiento=  request.json['fechanacimiento']
        genero =  request.json['genero']
        fcmtoken = request.json['tokenfcm']

        if codpersona == "0": #creo la persona
            mensagePer = consInsTabla('INSERT INTO personas (cedula, Apellidos, Nombres, FechaNacimiento, Genero, Estado, usuarioMod, fechaMod) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)',[cedula,apellido,nombre,fechanacimiento.replace("-",""),genero,'Activo',7,fecha])
            if mensagePer:
                persona =  consTablaPara("SELECT * FROM personas WHERE cedula=%s ",cedula)
                codpersona = persona[0][0]

        #crear contactos
        consInsTabla('INSERT INTO contactos (idPersona, Tipo, valor, estado, fechaIng, token) VALUES (%s,%s,%s,%s,%s,%s)',[codpersona,2,celular,'Activo',fecha,""])#celular tipo
        consInsTabla('INSERT INTO contactos (idPersona, Tipo, valor, estado, fechaIng, token) VALUES (%s,%s,%s,%s,%s,%s)',[codpersona,3,email,'Activo',fecha,""])#mail tipo
        consInsTabla('INSERT INTO contactos (idPersona, Tipo, valor, estado, fechaIng, token) VALUES (%s,%s,%s,%s,%s,%s)',[codpersona,7,fcmtoken,'Activo',fecha,""])#fcm tipo

        mensage = consInsTabla('INSERT INTO usuarios (Nombre, Email, Clave, TipoUsuario, Estado, fechaing, CodCondominio, celular,usuarioIng,UsuarioMod,public_id,codPersona) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',[apellido + " " + nombre,email,password,'1','Activo',fecha,0,celular,7,0,str(uuid4()),codpersona])
        if mensage:
            user = consTablaPara("SELECT * FROM usuarios WHERE email=%s ",req.get('email'))
            token_data ={
                'user_id' : user[0][11],
                'IdUsu' : user[0][0],
                'Nombre' : user[0][1],
                'Email' : user[0][2],
                'TipoUsuario' : user[0][4],
                'CodCondominio' : user[0][7],
                'Celular' : user[0][8],
                'codPersona' : user[0][12]
                
            }
        else:
             return jsonify({'mensage':'Usuario no creado.'})

        token = jwt.encode(token_data, app.config['SECRET_KEY'])
        return jsonify({'token':token.decode('UTF-8')})


    except Exception as error:
        return jsonify({
            'mensage':'Error al crear usuario.'
        }),400

@app.route("/visita", methods=['POST'])
@token_requerido
def visita(current_user):
    req = request.get_json(silent=True)
    if not req:
        return jsonify({
            'mensage':'No json data found.'
        })
    try:
        conjunto =  request.json['conjunto'] 
        etapa = request.json['etapa']
        casa = request.json['casa']
        user = current_user
        autorizado = request.json['autorizado']
        fechallegada = request.json['fechallegada'] 
        horallegada = request.json['horallegada']
        tipoReg = request.json['tipoReg']
        plataforma = request.json['plataforma']
        fecha = datetime.now().strftime("%Y%m%d")
        placa = request.json['placa']
        nrovisitantes = request.json['nrovisitantes']
        visitante = consTablaPara("SELECT codpersona FROM usuarios WHERE idusu=%s ",user)
        
        parametros =  [conjunto,etapa,casa,autorizado,fechallegada,horallegada,0,'',0,0,plataforma,'Activo',tipoReg,fecha,visitante,user,placa,nrovisitantes]
        mensage = consInsTabla('INSERT INTO visitas (idCondominio, idEtapa, idPropiedades, autorizada, fechaLLegada, horaLLegada, fechaSale, horaSale, fechaMod, usuarioMod, plataforma, estado, tipoReg, fechaReg,codvisita,usuarioreg,placa,nrovisitantes,horaIngresa) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,"")',parametros)
        if mensage:
            return jsonify(mensage)
        else:
             return jsonify({'mensage':'visita no creada'})

    except Exception as error:
        return jsonify({
            'mensage':'Error al crear la visita.'
        }),400

@app.route("/anulaVisita", methods=['POST'])
@token_requerido
def anulaVisita(current_user):
    
    req = request.get_json(silent=True)
    if not req:
        return jsonify({
            'mensage':'No json data found.'
        })
    try:
        idvisita =  request.json['idvisita'] 
        visita = current_user
        fecha = datetime.now().strftime("%Y%m%d")

        parametros =  [visita,fecha,'Cancelado',idvisita]
        mensage = consInsTabla('update visitas set usuarioMod = %s ,fechaMod = %s, estado = %s where idvisita = %s',parametros)
        if mensage:
            return jsonify(mensage)
        else:
             return jsonify({'mensage':'cancelacion erro'})

    except Exception as error:
        return jsonify({
            'mensage':'Error al cancelar la visita.'
        }),400

@app.route("/apruebaVisita", methods=['POST'])
@token_requerido
def apruebaVisita(current_user):
    
    req = request.get_json(silent=True)
    if not req:
        return jsonify({
            'mensage':'No json data found.'
        })
    try:
        conjunto =  request.json['conjunto'] 
        etapa = request.json['etapa']
        casa = request.json['casa']
        visita = current_user
        autorizado = request.json['autorizado']
        fechallegada = request.json['fechallegada'] 
        horallegada = request.json['horallegada']
        fecha = datetime.now().strftime("%Y%m%d")
        placa = request.json['placa']
        usuVisita = request.json['usuVisita']
        
        parametros =  [visita,fecha,autorizado,conjunto,etapa,casa,fechallegada,horallegada,usuVisita]
        mensage = consInsTabla('update visitas set usuarioMod = %s ,fechaMod = %s, autorizada = %s where idCondominio= %s and idEtapa= %s and idPropiedades= %s and fechaLLegada= %s and horaLLegada = %s and codvisita=%s',parametros)
        if mensage:
            return jsonify(mensage)
        else:
             return jsonify({'mensage':'Aprobación error'})

    except Exception as error:
        return jsonify({
            'mensage':'Error al crear la visita.'
        }),400

@app.route("/visitas")
@token_requerido
def visitas(current_user):
    
    fechacompleta = datetime.now()
    fechaNum = fechacompleta.strftime("%Y%m%d")
    data = consTabla("select idvisita, idCondominio, IFNULL((select Nombre from condominio where condominio.idCondominio = visitas.idCondominio),'Desc') as condominio, idEtapa, IFNULL((select NombreEtapa from etapas where idetapas = idEtapa),'Des') as etapa , idPropiedades,ifnull((select Nropropiedad + ' ' + nombre from propiedad where idPropiedad = idPropiedades),'Des') as propiedad, autorizada, fechaLLegada, horaLLegada, estado,placa,nrovisitantes,tipoReg,tipoProveedor,ifnull((select valor from parametros where coddefinicion = 'TipoProveedor' and codigo = tipoProveedor),'') as Proveedor from visitas  where estado = 'Activo' and fechallegada >= '"+str(fechaNum)+"' and usuarioreg ='" + str(current_user) + "' order by fechallegada,horaLLegada" )
    # data = consTabla ("select idvisita, idCondominio, IFNULL((select Nombre from condominio where condominio.idCondominio = visitas.idCondominio),'Desc') as condominio, idEtapa, IFNULL((select NombreEtapa from etapas where idetapas = idEtapa),'Des') as etapa , idPropiedades,ifnull((select Nropropiedad + ' ' + nombre from propiedad where idPropiedad = idPropiedades),'Des') as propiedad, autorizada, fechaLLegada, horaLLegada, estado from visitas")
    return json.dumps(data)


@app.route("/propiedades")
@token_requerido
def propiedades(current_user):
    data = consTabla ("select idPropiedad,Nropropiedad,nombre,idetapas, IFNULL((select NombreEtapa from etapas as e where e.idetapas = p.idEtapas),'No existe') as etapa,idResidencia, IFNULL((select Nombre from condominio as c where c.idCondominio = p.idResidencia),'No existe') as condominio from propiedad  as p where estado = 'activo'")
    return json.dumps(data)

@app.route("/condominios")
@token_requerido
def condominios(current_user):
    data = consTabla ("select idCondominio, Ruc, Nombre, Latitud, Longitud, Telefono, PaginaWeb, Logo from condominio where estado='activo';")
    return json.dumps(data)

@app.route("/etapas/<string:condominio_id>")
@token_requerido
def etapas(current_user,condominio_id):    
    data = consTablaParaL ("select idEtapas, NombreEtapa, idCondominio, DescripcionEtapa from etapas where estado = 'activo' and idCondominio =%s ",condominio_id)
    return json.dumps(data)


@app.route("/propiedad/<string:etapa_id>")
@token_requerido
def propiedad(current_user,etapa_id):    
    data = consTablaParaL ("select idPropiedad, idEtapas, idResidencia, TipoPropiedad,(select valor from parametros where CodDefinicion = 'TipoPropiedad'  and codigo = TipoPropiedad) as tipopro, Nropropiedad, metrosCuadrados, Nombre, Arrendada from propiedad where Estado = 'Activo' and idEtapas =%s ",etapa_id)
    return json.dumps(data) 

@app.route("/propiedadesPersona")
@token_requerido
def propiedadesPersona(current_user):    
    data = consTablaParaL ("select idPropiedad, idEtapas, idResidencia, TipoPropiedad,(select valor from parametros where CodDefinicion = 'TipoPropiedad'  and codigo = TipoPropiedad) as tipopro, Nropropiedad, metrosCuadrados, Nombre, Arrendada from propiedad where Estado = 'Activo' and idEtapas =%s ",etapa_id)
    return json.dumps(data) 


@app.route("/visitantes")
@token_requerido
def visitantes(current_user):
    fechacompleta = datetime.now()
    fechaNum = fechacompleta.strftime("%Y%m%d")
    usuario = consTablaPara("SELECT codpersona FROM usuarios WHERE idusu=%s ",str(current_user))
    data = consTabla("select idvisita, idCondominio, IFNULL((select Nombre from condominio where condominio.idCondominio = visitas.idCondominio),'Desc') as condominio, idEtapa, IFNULL((select NombreEtapa from etapas where idetapas = idEtapa),'Des') as etapa , idPropiedades,ifnull((select Nropropiedad + ' ' + nombre from propiedad where idPropiedad = idPropiedades),'Des') as propiedad, autorizada, fechaLLegada, horaLLegada, estado,placa,nrovisitantes,tipoReg,tipoProveedor,ifnull((select valor from parametros where coddefinicion = 'TipoProveedor' and codigo = tipoProveedor),'') as Proveedor,codvisita,IFNULL((select concat (Apellidos , ' ' , nombres)  from personas where codpersona = codvisita),'Desc') as VisitanteNombre from visitas  where estado in ('Activo','Ingreso') and fechallegada >= '"+str(fechaNum)+"' and idPropiedades in (select codPropiedad from copropietario where codpersona ="+str(usuario[0][0])+") order by fechallegada,horaLLegada, idCondominio, idEtapa, idPropiedades")
    return json.dumps(data)



@app.route("/fcmCopropietario/<string:tipo>/<string:propiedad>")
@token_requerido
def fcmCopropietario(current_user,tipo,propiedad):  
    if tipo == "p":  
        data = consTablaParaL ("select codpersona,valor from copropietario , contactos where codPersona = idpersona and contactos.tipo = 7 and not valor = '' and codPropiedad = %s ",propiedad)
    else:
        data = consTablaParaL ("select idpersona,valor from contactos where tipo = 7 and not valor = '' and idpersona = %s ",propiedad)

    return json.dumps(data)


@app.route("/productos")
def productos():    
    data = consTabla ("select idproducto,nombre,  CONVERT(precio, CHAR), CASE WHEN precio < 15 THEN CONVERT(precio *1.20,char) WHEN precio >= 15 and precio < 40 THEN CONVERT(precio * 1.15,char) WHEN precio >= 40 and precio < 100 THEN CONVERT(precio * 1.12,char) ELSE CONVERT(precio * 1.10,char) END as pvp, imagen, stock, codproveedor, promocion from productos.producto ")
    return json.dumps(data) 

@app.route("/producto/<string:busca>")
def producto(busca):
    data = consTabla (" select idproducto,nombre,  CONVERT(precio, CHAR), CASE WHEN precio < 15 THEN CONVERT(precio *1.20,char) WHEN precio >= 15 and precio < 40 THEN CONVERT(precio * 1.15,char) WHEN precio >= 40 and precio < 100 THEN CONVERT(precio * 1.12,char) ELSE CONVERT(precio * 1.10,char) END as pvp, imagen, stock, codproveedor, promocion from productos.producto where nombre LIKE '%"+ busca + "%' order by nombre;  ")
    return json.dumps(data) 


@app.route("/claveapp", methods=['POST'])
def claveapp():
    req = request.get_json(silent=True)
    if not req:
        return jsonify({
            'mensage':'No json data found.'
        })
    try:
        token =  request.json['token'] 
        parametros =  [token,'Activo']
        mensage = consInsTabla('INSERT INTO firebase (token, estado) values (%s,%s)',parametros)
        if mensage:
            return jsonify(mensage)
        else:
             return jsonify({'mensage':'error token'})

    except Exception as error:
        return jsonify({
            'mensage':'Error al crear el token firebase.'
        }),400

@app.route("/notificaciones", methods=['POST'])
@token_requerido
def notificaciones(current_user):
    req = request.get_json(silent=True)
    
    if not req:
        return jsonify({
            'mensage':'No json data found.'
        })
    try:
        token =  request.json['token'] 
        titulo =  request.json['titulo'] 
        mensaje =  request.json['mensaje'] 
        datos =  request.json['datos']

        headers = {
            'Authorization': 'key=AAAAAU4X5hE:APA91bEguRwlVoGAmwjlI6UQP4YeYf543SSEMuLIN5r05-7FWGdJZNQJFvVmvsxixaJI0ZCnCZZ9JWcsC_sLPzr50fTgHiFIiFuO6eCFTWmv_yyDsJsPjcBtN4lH2xowZCTcVGtc-VqT',
            'Content-Type': 'application/json'
        }
        url = 'https://fcm.googleapis.com/fcm/send'
        payload = {
            "to": token,
            "notification": {
                "body": mensaje,
                "title": titulo
                },
            "data": datos
        }
        resp = requests.post(url, headers=headers, data=json.dumps(payload))
        if resp.status_code == 200:
            return jsonify({'mensage':'ok'})
        else:
             return jsonify({'mensage':'error notificacion'})

    except Exception as error:
        return jsonify({
            'mensage':'Error al crear la notificacion.'
        }),400

@app.route("/buscaPersona", methods=['POST'])
def buscaPersona(): 
    req = request.get_json(silent=True)
    if not req:
        return jsonify({
            'mensage':'No json data found.'
        })
    try:
        cedula =  request.json['cedula'] 
        
        data = consTabla (" select CodPersona, cedula, Apellidos, Nombres, FechaNacimiento, Genero from personas where estado = 'activo' and cedula = '" + cedula + "'" )
        return json.dumps(data)
        

    except Exception as error:
        return jsonify({
            'mensage':'Error al consultar la persona.'
        }),400

