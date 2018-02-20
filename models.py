import random
import string
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine, func
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import(TimedJSONWebSignatureSerializer as
                         Serializer, BadSignature, SignatureExpired)

Base = declarative_base()
key_helper = random.choice(string.ascii_uppercase + string.digits)
secret_key = ''.join(key_helper for x in xrange(32))


# User Model
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    g_id = Column(String(64))
    name = Column(String(64))


# Category Model
class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    items = relationship("Item", cascade="all, delete-orphan")

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
            'items': [i.serialize for i in self.items],

        }


# Item Model
class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    description = Column(String(250))
    category = relationship(Category)
    cat_id = Column(Integer, ForeignKey('category.id'))
    time = Column(DateTime, server_default=func.now())

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
        }


engine = create_engine('sqlite:///itemCatalog.db')

Base.metadata.create_all(engine)
