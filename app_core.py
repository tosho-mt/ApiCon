""" App core """

from flask import Flask, request, jsonify
# from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
# from flask_marshmallow import Marshmallow
# from flask_migrate import Migrate


app = Flask(__name__)
app.config['MYSQL_DATABASE_HOST']='localhost'
app.config['MYSQL_DATABASE_USER']='root'
app.config['MYSQL_DATABASE_PASSWORD']='sisfiab'
app.config['MYSQL_DATABASE_DB']='condominio'

# app.config['MYSQL_DATABASE_HOST']='b2upkzc8ezoaq4qyocyd-mysql.services.clever-cloud.com'
# app.config['MYSQL_DATABASE_USER']='uovvjbjmxz6gbzvm'
# app.config['MYSQL_DATABASE_PASSWORD']='2UgT6FPsi2rtXJyjswyw'
# app.config['MYSQL_DATABASE_DB']='b2upkzc8ezoaq4qyocyd'


bcrypt = Bcrypt(app)

### esto es con sqllike
app.config['SECRET_KEY'] = 'SisFiabIeAcT'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/MauricioT/Desktop/apicon/db/dataPruebaApi.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

### esto es con mysql
# app.config['SQLALCHEMY_DATABASE_URI'] ='mysql+pymysql://root:SisFiab@localhost:3306/flaskmysql'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# db = SQLAlchemy(app)
# ma = Marshmallow(app)
# migrate = Migrate(app,db)

#controlar errores rutas no existentes y mas
@app.errorhandler(404)
def page_not_found(err):
        return jsonify({'mensage':'inicio API, Ruta no existe'})








