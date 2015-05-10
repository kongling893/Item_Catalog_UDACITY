from flask import Flask, render_template, request, redirect, jsonify, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, ToyShop, ToyItem

app = Flask(__name__)

engine = create_engine('sqlite:///toyshop.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession(


@app.route('/')
@app.route('/index')
def index():
	return "hello"

if __name__ == '__main__':
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)
