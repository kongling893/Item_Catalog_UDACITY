import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
	__tablename__ = 'user'

	id = Column(Integer, primary_key=True)
	name = Column(String(250), nullable=False)
	email = Column(String(250), nullable=False)
	picture = Column(String(250))

	@property
	def serialize(self):
		"""Return object data in easily serializeable format"""
		return {
			'name': self.name,
			'email': self.email,
			'id': self.id,
			'picture': self.picture,
		}

class ToyShop(Base):
	__tablename__ = 'toy_shop'
	id = Column(Integer, primary_key=True)
	name = Column(String(250), nullable=False)
	description = Column(String(250))
	user_id = Column(Integer, ForeignKey('user.id'))
	user = relationship(User)

	@property
	def serialize(self):
		"""Return object data in easily serializeable format"""
		return {
			'name': self.name,
			'description': self.description,
			'id': self.id,
			'user_id': self.user_id,
		}

class ToyItem(Base):
	__tablename__ = 'toy_item'

	name = Column(String(80), nullable=False)
	id = Column(Integer, primary_key=True)
	description = Column(String(250))
	price = Column(String(8))
	shop_id = Column(Integer, ForeignKey('toy_shop.id'))
	shop = relationship(ToyShop)
	user_id = Column(Integer, ForeignKey('user.id'))
	user = relationship(User)

	@property
	def serialize(self):
		"""Return object data in easily serializeable format"""
		return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'price': self.price,
        }


engine = create_engine('postgresql://catalog:catalog123@localhost/catalog')

Base.metadata.create_all(engine)
