# Debugging
from __future__ import print_function
import sys

from models import User, Category, Item, Base
from flask import Flask, jsonify, request, url_for, abort, g, render_template, session, redirect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

from flask_httpauth import HTTPBasicAuth
import json

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
from flask import make_response
import requests

# Authentication
auth = HTTPBasicAuth()

# Connect to Database and create database session
engine = create_engine('sqlite:///itemCatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
db = DBSession()


# Start Flask
app = Flask(__name__, static_url_path='/static')

# Get Client ID
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']


# Show Main Page
@app.route('/')
@app.route('/app')
def showIndex():
    categories = db.query(Category).all()
    items = db.query(Item).order_by(Item.time.desc()).all()
    return render_template('index.html', categories=categories, items=items, home=True)

# Show Item Descriptions

@app.route('/app/<cName>/<iName>')
def showItemDesc(cName, iName):
    item = db.query(Item).filter_by(name=iName).one()
    return render_template('desc.html', item=item)

# Show All Items In Category

@app.route('/app/<cName>')
def showItems(cName):
    cat = db.query(Category).filter_by(name=cName).one()
    categories = db.query(Category).all()
    items = db.query(Item).filter_by(cat_id=cat.id).all()
    iNum = len(items)
    return render_template('index.html', categories=categories, items=items, home=False, cat=cat, iNum=iNum)

@app.route('/signout', methods = ['GET'])
def logout():
    session['g_id'] = None
    print("Signed out!", file = sys.stderr)
    return redirect("http://localhost:1234/", code=301)

@app.route('/oauth/<provider>', methods = ['POST'])
def login(provider):
    # STEP 1 - Parse the auth code
    auth_code = request.data
    print(auth_code, file=sys.stderr)
    if provider == 'google':
        # STEP 2 - Exchange for a token
        try:
            # Upgrade the authorization code into a credentials object
            oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
            oauth_flow.redirect_uri = 'postmessage'
            credentials = oauth_flow.step2_exchange(auth_code)
        except FlowExchangeError:
            response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
            response.headers['Content-Type'] = 'application/json'
            return response
          
        # Check that the access token is valid.
        access_token = credentials.access_token
        url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
        h = httplib2.Http()
        result = json.loads(h.request(url, 'GET')[1])
        # If there was an error in the access token info, abort.
        if result.get('error') is not None:
            response = make_response(json.dumps(result.get('error')), 500)
            response.headers['Content-Type'] = 'application/json'
            
        # # Verify that the access token is used for the intended user.
        g_id = credentials.id_token['sub']
        if result['user_id'] != g_id:
            response = make_response(json.dumps("Token's user ID doesn't match given user ID."), 401)
            response.headers['Content-Type'] = 'application/json'
            return response

        # # Verify that the access token is valid for this app.
        if result['issued_to'] != CLIENT_ID:
            response = make_response(json.dumps("Token's client ID does not match app's."), 401)
            response.headers['Content-Type'] = 'application/json'
            return response

        stored_g_id = session.get('g_id')
        if g_id == stored_g_id:
            response = make_response(json.dumps('Current user is already connected.'), 200)
            response.headers['Content-Type'] = 'application/json'
            return response

        # STEP 3 - Find User or make a new one
        
        # Get user info
        h = httplib2.Http()
        userinfo_url =  "https://www.googleapis.com/oauth2/v1/userinfo"
        params = {'access_token': credentials.access_token, 'alt':'json'}
        answer = requests.get(userinfo_url, params=params)
      
        data = answer.json()

        user_name = data['name']
        user_id = data['id']
        # See if user exists, if it doesn't make a new one
        exists = db.query(User.id).filter_by(id = 2).scalar() is not None
        if exists:
            user = db.query(User).filter_by(g_id=user_id).first()
        if not exists or not user:
            user = User(g_id = user_id, name = user_name)
            db.add(user)
            db.commit()

        # STEP 4 - Make token
        token = user.generate_auth_token(600)

        # STEP 5 - Make user session

        session['g_id'] = g_id

        # STEP 6 - Send back token to the client 

        return jsonify({'token': token.decode('ascii'), 'duration': 600})
    else:
        return 'Unrecoginized Provider'

@app.route('/api/resource')
@auth.login_required
def get_resource():
    return jsonify({ 'data': 'Hello, %s!' % g.user.username })



# Create a new menu item
# @app.route('/restaurant/<int:restaurant_id>/menu/new/', methods=['GET', 'POST'])
# def newMenuItem(restaurant_id):
#     restaurant = db.query(Restaurant).filter_by(id=restaurant_id).one()
#     if request.method == 'POST':
#         newItem = MenuItem(name=request.form['name'], description=request.form[
#                            'description'], price=request.form['price'], course=request.form['course'], restaurant_id=restaurant_id)
#         db.add(newItem)
#         db.commit()
#         flash('New Menu %s Item Successfully Created' % (newItem.name))
#         return redirect(url_for('showMenu', restaurant_id=restaurant_id))
#     else:
#         return render_template('newmenuitem.html', restaurant_id=restaurant_id)


# # JSON APIs to view Restaurant Information
# @app.route('/restaurant/<int:restaurant_id>/menu/JSON')
# def restaurantMenuJSON(restaurant_id):
#     restaurant = db.query(Restaurant).filter_by(id=restaurant_id).one()
#     items = db.query(MenuItem).filter_by(
#         restaurant_id=restaurant_id).all()
#     return jsonify(MenuItems=[i.serialize for i in items])


# @app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON')
# def menuItemJSON(restaurant_id, menu_id):
#     Menu_Item = db.query(MenuItem).filter_by(id=menu_id).one()
#     return jsonify(Menu_Item=Menu_Item.serialize)


# @app.route('/restaurant/JSON')
# def restaurantsJSON():
#     restaurants = db.query(Restaurant).all()
#     return jsonify(restaurants=[r.serialize for r in restaurants])

# Create a new restaurant


# @app.route('/restaurant/new/', methods=['GET', 'POST'])
# def newRestaurant():
#     if request.method == 'POST':
#         newRestaurant = Restaurant(name=request.form['name'])
#         db.add(newRestaurant)
#         flash('New Restaurant %s Successfully Created' % newRestaurant.name)
#         db.commit()
#         return redirect(url_for('showRestaurants'))
#     else:
#         return render_template('newRestaurant.html')

# # Edit a restaurant


# @app.route('/restaurant/<int:restaurant_id>/edit/', methods=['GET', 'POST'])
# def editRestaurant(restaurant_id):
#     editedRestaurant = db.query(
#         Restaurant).filter_by(id=restaurant_id).one()
#     if request.method == 'POST':
#         if request.form['name']:
#             editedRestaurant.name = request.form['name']
#             flash('Restaurant Successfully Edited %s' % editedRestaurant.name)
#             return redirect(url_for('showRestaurants'))
#     else:
#         return render_template('editRestaurant.html', restaurant=editedRestaurant)


# # Delete a restaurant
# @app.route('/restaurant/<int:restaurant_id>/delete/', methods=['GET', 'POST'])
# def deleteRestaurant(restaurant_id):
#     restaurantToDelete = db.query(
#         Restaurant).filter_by(id=restaurant_id).one()
#     if request.method == 'POST':
#         db.delete(restaurantToDelete)
#         flash('%s Successfully Deleted' % restaurantToDelete.name)
#         db.commit()
#         return redirect(url_for('showRestaurants', restaurant_id=restaurant_id))
#     else:
#         return render_template('deleteRestaurant.html', restaurant=restaurantToDelete)



# # Edit a menu item


# @app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit', methods=['GET', 'POST'])
# def editMenuItem(restaurant_id, menu_id):

#     editedItem = db.query(MenuItem).filter_by(id=menu_id).one()
#     restaurant = db.query(Restaurant).filter_by(id=restaurant_id).one()
#     if request.method == 'POST':
#         if request.form['name']:
#             editedItem.name = request.form['name']
#         if request.form['description']:
#             editedItem.description = request.form['description']
#         if request.form['price']:
#             editedItem.price = request.form['price']
#         if request.form['course']:
#             editedItem.course = request.form['course']
#         db.add(editedItem)
#         db.commit()
#         flash('Menu Item Successfully Edited')
#         return redirect(url_for('showMenu', restaurant_id=restaurant_id))
#     else:
#         return render_template('editmenuitem.html', restaurant_id=restaurant_id, menu_id=menu_id, item=editedItem)


# # Delete a menu item
# @app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete', methods=['GET', 'POST'])
# def deleteMenuItem(restaurant_id, menu_id):
#     restaurant = db.query(Restaurant).filter_by(id=restaurant_id).one()
#     itemToDelete = db.query(MenuItem).filter_by(id=menu_id).one()
#     if request.method == 'POST':
#         db.delete(itemToDelete)
#         db.commit()
#         flash('Menu Item Successfully Deleted')
#         return redirect(url_for('showMenu', restaurant_id=restaurant_id))
#     else:
#         return render_template('deleteMenuItem.html', item=itemToDelete)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=1234)