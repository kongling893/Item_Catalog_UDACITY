from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, FoodTruck, MenuItem, User
from flask import session as login_session
from flask import make_response, jsonify, url_for, flash
from flask import Flask, render_template, request, redirect
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import requests
import httplib2
import json
import random
import string
app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Food Truck Menu Application"

engine = create_engine('sqlite:///food_truck_database.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create a state token to prevent request forgery.
# Store it in the session for later validation


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(
        string.ascii_uppercase + string.digits
        ) for x in xrange(32))
    login_session['state'] = state
    # return state
    return render_template('login.html', STATE=state)


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
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps(
            'Failed to upgrade the authorization code.'
            ), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
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
    gplus_id = credentials.id_token['sub']
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
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id
    response = make_response(json.dumps('Successfully connected user.', 200))

    print "#Get user info"
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
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

# DISCONNECT - Revoke a current user's token and reset their login_session


@app.route("/gdisconnect")
def gdisconnect():
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
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
        return response
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(json.dumps(
            'Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response




# JSON APIs to view Food Truck Information
@app.route('/food_truck/<int:food_truck_id>/menu/JSON')
def food_truckMenuJSON(food_truck_id):
    food_truck = session.query(FoodTruck).filter_by(id=food_truck_id).one()
    items = session.query(MenuItem).filter_by(
        food_truck_id=food_truck_id).all()
    return jsonify(MenuItems=[i.serialize for i in items])


@app.route('/food_truck/<int:food_truck_id>/menu/<int:menu_id>/JSON')
def menuItemJSON(food_truck_id, menu_id):
    Menu_Item = session.query(MenuItem).filter_by(id=menu_id).one()
    return jsonify(Menu_Item=Menu_Item.serialize)


@app.route('/food_truck/JSON')
def food_trucksJSON():
    food_trucks = session.query(FoodTruck).all()
    return jsonify(food_trucks=[r.serialize for r in food_trucks])


# Show all food trucks
@app.route('/')
@app.route('/food_truck/')
def showFoodTrucks():
    food_trucks = session.query(FoodTruck).order_by(asc(FoodTruck.name))

    credentials = login_session.get('credentials')

    if credentials is None:
        login_status = "not logged in"
        login_user_id = 0
        login_username = "no username"
    else:
        login_status = "logged in"
        login_user_id = getUserID(login_session['email'])
        login_username = login_session['username']
    print "login_status:"
    print login_status


    return render_template(
        'food_trucks.html',
        food_trucks=food_trucks,
        login_status=login_status,
        login_user_id=login_user_id,
        login_username=login_username
        )


# Create a new food truck
@app.route('/food_truck/new/', methods=['GET', 'POST'])
def newFoodTruck():
    credentials = login_session.get('credentials')
    if credentials is None:
        flash('You must login to create a food truck')
        return redirect(url_for('showFoodTrucks'))
    else:
        if request.method == 'POST':
            login_user_id = getUserID(login_session['email'])
            newFoodTruck = FoodTruck(
                name=request.form['name'], user_id_database=login_user_id)
            session.add(newFoodTruck)
            flash('New Food Truck %s Successfully Created' % newFoodTruck.name)
            session.commit()
            return redirect(url_for('showFoodTrucks'))
        else:
            return render_template('newFoodTruck.html')


# Edit a food Truck
@app.route('/food_truck/<int:food_truck_id>/edit/', methods=['GET', 'POST'])
def editFoodTruck(food_truck_id):
    credentials = login_session.get('credentials')
    login_user_id = getUserID(login_session['email'])
    editedFoodTruck = session.query(FoodTruck).filter_by(
        id=food_truck_id).one()
    if editedFoodTruck.user_id_database != login_user_id:
        flash("You can only edit food trucks you have created.")
        return redirect(url_for('showFoodTrucks'))
    else:
        if request.method == 'POST':
            if request.form['name']:
                editedFoodTruck.name = request.form['name']
                flash(
                    'Food Truck Successfully Edited: %s'
                    % editedFoodTruck.name)
                return redirect(url_for('showFoodTrucks'))
        else:
            return render_template(
                'editFoodTruck.html', food_truck=editedFoodTruck)


# Delete a food_truck
@app.route('/food_truck/<int:food_truck_id>/delete/', methods=['GET', 'POST'])
def deleteFoodTruck(food_truck_id):
    credentials = login_session.get('credentials')
    login_user_id = getUserID(login_session['email'])
    food_truckToDelete = session.query(FoodTruck).filter_by(
        id=food_truck_id).one()
    print "truck:"
    print food_truckToDelete.user_id_database
    print "user_id:"
    print login_user_id

    if request.method == 'POST':
        session.delete(food_truckToDelete)
        flash('%s Successfully Deleted' % food_truckToDelete.name)
        session.commit()
        return redirect(url_for(
            'showFoodTrucks', food_truck_id=food_truck_id))
    else:
        # return render_template(
        # 'deleteFoodTruck.html',food_truck = food_truckToDelete)
        return redirect(url_for(
            'showFoodTrucks', food_truck_id=food_truck_id))


# Show a food_truck menu
@app.route('/food_truck/<int:food_truck_id>/')
@app.route('/food_truck/<int:food_truck_id>/menu/')
def showMenu(food_truck_id):
    food_truck = session.query(FoodTruck).filter_by(id=food_truck_id).one()
    items = session.query(MenuItem).filter_by(
        food_truck_id=food_truck_id).all()
    return render_template(
        'menu.html', items=items, food_truck=food_truck)


# Create a new menu item
@app.route(
    '/food_truck/<int:food_truck_id>/menu/new/', methods=['GET', 'POST'])
def newMenuItem(food_truck_id):
    food_truck = session.query(FoodTruck).filter_by(id=food_truck_id).one()
    if request.method == 'POST':
        newItem = MenuItem(
            name=request.form['name'],
            description=request.form['description'],
            price=request.form['price'],
            course=request.form['course'],
            food_truck_id=food_truck_id)
        session.add(newItem)
        session.commit()
        flash('New Menu %s Item Successfully Created' % (newItem.name))
        return redirect(
            url_for('showMenu', food_truck_id=food_truck_id))
    else:
        return render_template(
            'newmenuitem.html', food_truck_id=food_truck_id)


# Edit a menu item
@app.route(
    '/food_truck/<int:food_truck_id>/menu/<int:menu_id>/edit',
    methods=['GET', 'POST'])
def editMenuItem(food_truck_id, menu_id):
    editedItem = session.query(MenuItem).filter_by(id=menu_id).one()
    food_truck = session.query(FoodTruck).filter_by(id=food_truck_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['price']:
            editedItem.price = request.form['price']
        if request.form['course']:
            editedItem.course = request.form['course']
        session.add(editedItem)
        session.commit()
        flash('Menu Item Successfully Edited')
        return redirect(url_for('showMenu', food_truck_id=food_truck_id))
    else:
        return render_template(
            'editmenuitem.html',
            food_truck_id=food_truck_id,
            menu_id=menu_id,
            item=editedItem)


# Delete a menu item
@app.route(
    '/food_truck/<int:food_truck_id>/menu/<int:menu_id>/delete',
    methods=['GET', 'POST'])
def deleteMenuItem(food_truck_id, menu_id):
    food_truck = session.query(FoodTruck).filter_by(id=food_truck_id).one()
    itemToDelete = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Menu Item Successfully Deleted')
        return redirect(url_for('showMenu', food_truck_id=food_truck_id))
    else:
        return render_template('deleteMenuItem.html', item=itemToDelete)


@app.route('/test_jinja_if')
def test_jinja_if():
    credentials = login_session.get('credentials')
    if credentials is None:
        login_status = "not logged in"
    else:
        login_status = "logged in"
        #login_user_id = getUserID(login_session['email'])
    print "login_status:"
    print login_status
    return render_template('test_jinja_if.html', login_status=login_status)


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def createUser(login_session):
    newUser = User(
        name=login_session['username'],
        email=login_session['email'],
        picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
# item_catalog
