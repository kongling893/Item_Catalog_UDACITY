
from flask import Flask, jsonify,render_template, request, redirect, jsonify, url_for, flash
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, ToyShop, ToyItem, User
from functions_helper import *
import random, string

from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

import os

path = os.path.dirname(__file__)

app = Flask(__name__)
CLIENT_ID = json.loads(open(path+'/client_secrets.json', 'r').read())['web']['client_id']

engine = create_engine('postgresql://catalog:catalog123@localhost/catalog')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/index/')
def showShops():
	toyshops = session.query(ToyShop).all()
	return render_template("main.html",toyshops = toyshops, login_session = login_session )


@app.route('/index/<string:shop_ID>/')
def showItems(shop_ID):
	toyshop = session.query(ToyShop).filter_by(id=shop_ID).one()
	user_id = toyshop.user_id
	user = session.query(User).filter_by(id = user_id).one()
	toys = session.query(ToyItem).filter_by(shop_id=shop_ID).all()
	return render_template('toys.html', toys=toys, toyshop=toyshop, user = user, login_session = login_session)


@app.route('/login/')
def login():
	state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
	login_session['state'] = state
	return render_template('login.html',STATE=state, login_session = login_session)

		
@app.route('/gconnect', methods=['POST'])
def gconnect():
    print 'received state of %s' % request.args.get('state')
    print 'login_sesion["state"] = %s' % login_session['state']
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    gplus_id = request.args.get('gplus_id')
    print "request.args.get('gplus_id') = %s" % request.args.get('gplus_id')
    code = request.data
    print "received code of %s " % code

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets(path+'/client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
        
    except FlowExchangeError:
        response = make_response(json.dumps(
            'Failed to upgrade the authorization code.'
            ), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    credentials = credentials.to_json()            
    credentials = json.loads(credentials)         
    access_token = credentials['token_response']['access_token']     
    url = (
        'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
        % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials['id_token']['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'
            ), 200)
        response.headers['Content-Type'] = 'application/json'

    # Store the access token in the session for later use.
    login_session['provider'] = 'google'
    response = make_response(json.dumps('Successfully connected user.', 200))

    print "#Get user info"
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials['token_response']['access_token'], 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = json.loads(answer.text)

    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id
    login_session['username'] = data["name"]
    login_session['picture'] = data["picture"]
    login_session['email'] = data["email"]
    print login_session['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    # dimensions of the picture at login:
    output += ' " style = "width: 300px; height: \
        300px;border-radius: \
        50px;-webkit-border-radius: \
        150px;-moz-border-radius: 50px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    return output


@app.route("/gdisconnect")
def gdisconnect():
    credentials = login_session.get('credentials')
    # Only disconnect a connected user.
    if not checkLogin(login_session):
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials['token_response']['access_token']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset the user's session.
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash('Successfully disconnected.')
        return redirect(url_for('showShops'))
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(json.dumps(
            'Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        flash('Failed to revoke token for given user.')
        return redirect(url_for('showShops'))


# Create a new shop
@app.route('/new/', methods=['GET', 'POST'])
def newShop():
	if not checkLogin(login_session):
		flash('You must login to create a toy shop')
		return redirect(url_for('showShops'))
	
	if request.method == 'POST':
		
		newShop = ToyShop(name=request.form['name'],description = request.form['description'], user_id = login_session.get('user_id') )
		session.add(newShop)
		flash('New Toy shop %s Successfully Created' % newShop.name)
		session.commit()
		return redirect(url_for('showShops'))
	else:
		return render_template('newshop.html',login_session = login_session)

# add a new toy to shop
@app.route('/index/<string:shop_ID>/add', methods=['GET', 'POST'])
def addNewToy(shop_ID):
	if not checkLogin(login_session):
		flash('You must login to create a toy shop')
		return redirect(url_for('showShops'))
	if request.method == 'POST':
		newToy = ToyItem(name=request.form['name'],
						description = request.form['description'], 
						user_id = login_session.get('user_id'), 
						price = request.form['price'], 
						shop_id = shop_ID)
		session.add(newToy)
		session.commit()
		flash('New Toy %s has been successfully Created' % newToy.name)
		return redirect(url_for('showItems',shop_ID = shop_ID))
	else:
		return render_template('newtoy.html',shop_ID = shop_ID,login_session = login_session)

# delete a toy from shop
@app.route('/index/<string:shop_ID>/<string:toy_ID>/delete')
def deleteToy(shop_ID,toy_ID):
	if not checkLogin(login_session):
		flash('You must login to manage a toy shop.')
		return redirect(url_for('showItems',shop_ID = shop_ID))
	login_user_id = getUserID(login_session['email'])
	toyToDelete = session.query(ToyItem).filter_by(id=toy_ID).one()
	if toyToDelete.user_id != login_user_id:
		flash("You can only manage your own shop.")
		return redirect(url_for('showItems',shop_ID = shop_ID))
	session.delete(toyToDelete)
	session.commit()
	flash("You have managed your shop successfully.")
	return redirect(url_for('showItems',shop_ID = shop_ID))

# edit a toy
@app.route('/index/<string:shop_ID>/<string:toy_ID>/edit', methods=['GET', 'POST'])
def editToy(shop_ID,toy_ID):
	if not checkLogin(login_session):
		flash('You must login to manage a toy shop.')
		return redirect(url_for('showItems',shop_ID = shop_ID))
	login_user_id = getUserID(login_session['email'])
	toyToEdite = session.query(ToyItem).filter_by(id=toy_ID).one()
	if toyToEdite.user_id != login_user_id:
		flash("You can only manage your own shop.")
		return redirect(url_for('showItems',shop_ID = shop_ID))
	if request.method == 'POST':
		toyToEdite.name = request.form['name']
		toyToEdite.description = request.form['description']
		toyToEdite.price = request.form['price']
		flash('%s has been successfully edited' % toyToEdite.name)
		return redirect(url_for('showItems',shop_ID = shop_ID))
	else:
		return render_template('editToy.html',toy = toyToEdite,login_session = login_session)

# edit a toy shop
@app.route('/index/<string:shop_ID>/edit', methods=['GET', 'POST'])
def editToyshop(shop_ID):
	if not checkLogin(login_session):
		flash('You must login to manage a toy shop.')
		return redirect(url_for('showItems',shop_ID = shop_ID))
	login_user_id = getUserID(login_session['email'])
	shopToEdit = session.query(ToyShop).filter_by(id=shop_ID).one()
	if shopToEdit.user_id != login_user_id:
		flash("You can only manage your own shop.")
		return redirect(url_for('showItems',shop_ID = shop_ID))
	if request.method == 'POST':
		shopToEdit.name = request.form['name']
		shopToEdit.description = request.form['description']
		flash('%s has been successfully edited' % shopToEdit.name)
		return redirect(url_for('showItems',shop_ID = shop_ID))
	else:
		return render_template('editShop.html',toyShop = shopToEdit,login_session = login_session)

# delete a toy shop
@app.route('/index/<string:shop_ID>/delete/')
def deleteToyshop(shop_ID):
	if not checkLogin(login_session):
		flash('You must login to manage a toy shop.')
		return redirect(url_for('showItems',shop_ID = shop_ID))
	login_user_id = getUserID(login_session['email'])
	ShopToDelete = session.query(ToyShop).filter_by(id=shop_ID).one()
	if ShopToDelete.user_id != login_user_id:
		flash("You can only delete your own shop.")
		return redirect(url_for('showShops'))
	session.delete(ShopToDelete)
	session.commit()
	flash("You have deleted your shop successfully.")
	return redirect(url_for('showShops'))


@app.route('/help/')
def help():
	return render_template("help.html")

#json APIs
@app.route('/index/<string:shop_ID>/JSON/')
def shopJSON(shop_ID):
    shops = session.query(ToyShop).filter_by(id=shop_ID).one()
    toys = session.query(ToyItem).filter_by(shop_id = shop_ID).all()
    return jsonify(Shop=shops.serialize, Toys = [g.serialize for g in toys])


@app.route('/index/<string:shop_ID>/<string:toy_ID>/JSON/')
def toyJSON(shop_ID,toy_ID):
    toy = session.query(ToyItem).filter_by(id=toy_ID).one()
    return jsonify(Toy = toy.serialize)

if __name__ == '__main__':
	app.secret_key = 'super secret key'
	app.debug = True
	app.run(host = 'localhost', port = 5000)
