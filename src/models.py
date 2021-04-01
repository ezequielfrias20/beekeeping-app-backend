from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.security import generate_password_hash, check_password_hash
from base64 import b64encode

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String(120),nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    hashed_password = db.Column(db.String(80), unique=False, nullable=False)    
    salt=db.Column(db.String(200),nullable=False)
    sales=db.relationship("Sale",backref="user")

    def __init__(self,body):
        self.name=body['name']
        self.email=body['email']
        self.salt=b64encode(os.urandom(4)).decode("utf-8")
        self.hashed_password=set_password(body['password'])

    @classmethod
    def create(cls,**kwargs):
        new_user=cls(kwargs)
        db.session.add(new_user)
        db.session.commit()
        return new_user

    def set_password(self,password):
        return generate_password_hash(
            f"{password}{self.salt}"
        )

    def check_password(self, password):
        print(f"este es el password:{password}")
        return check_password_hash(
            self.hashed_password,
            f"{password}{self.salt}"
        )
        
    def serialize(self):
        return {
            "id": self.id,
            "name":self.name,
            "email": self.email,
            # do not serialize the password, its a security breach
        }
    
class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date= db.Column(db.Integer(120),nullable=False)
    description=db.Column(db.String(120), unique=True, nullable=False)
    money_USD = db.Column(db.String(120), unique=True, nullable=False)

    user_id=db.Column(db.Integer, db.ForeignKey('user.id'))


    def __init__(self,body):
        self.date=body['date']
        self.description=body['description']
        self.money_USD=body['money_USD']

    @classmethod
    def create(cls,**kwargs):
        new_sale=cls(kwargs)
        db.session.add(new_sale)
        db.session.commit()
        return new_sale

        
    def serialize(self):
        return {
            "id": self.id,
            "date":self.date,
            "description": self.description,
            "money_USD"=self.money_USD
            # do not serialize the password, its a security breach
        }