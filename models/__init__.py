### modelos ###
from uuid import uuid4
from app_core import db, ma ,bcrypt


class User(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(500),unique=True,nullable=True)
    email = db.Column(db.String(100),unique=True,nullable=True)
    password = db.Column(db.String(1000),nullable=True)
    is_admin= db.Column(db.Boolean,default=False)




    def __init__(self,email,password,is_admin=False):
        self.public_id=str(uuid4())
        self.email = email
        self.password= bcrypt.generate_password_hash(password)
        self.is_admin= is_admin


    def check_password(self,password):
        return bcrypt.check_password_hash(self.password,password) 

    def as_dict(self):
        return{
            "id":self.public_id,
            "mail":self.email,    
            "is_admin":self.is_admin     
        }

db.create_all()

class UserSchema(ma.Schema):
    class Meta:
        fields = ('id','public_id', 'email', 'password','is_admin')

user_schema = UserSchema()
users_schema = UserSchema(many=True)