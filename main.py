""" jwt test app """

from app_core import app
from routes import *

# from models import *
# from flask_marshmallow import Marshmallow


# db.create_all()

if __name__ == '__main__':
    # app.run(debug=True, threaded=True )
    # app.run(debug=True, threaded=True ,port = 3000 , host="192.168.1.12")
    app.run(debug=True, threaded=True ,port = 3000 , host="192.168.1.11")