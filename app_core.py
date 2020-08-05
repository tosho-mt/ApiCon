""" App core """

from flask import Flask, request, jsonify
# from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
# from flask_marshmallow import Marshmallow
# from flask_migrate import Migrate


app = Flask(__name__)
app.config['MYSQL_DATABASE_HOST']='localhost'
app.config['MYSQL_DATABASE_USER']='root'
app.config['MYSQL_DATABASE_PASSWORD']='SisFiab'
app.config['MYSQL_DATABASE_DB']='condominio'
bcrypt = Bcrypt(app)

### esto es con sqllike
app.config['SECRET_KEY'] = 'SisFiamIeAcT'
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








