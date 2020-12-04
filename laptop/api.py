# Laptop Service
from flask import Flask, jsonify, request, render_template, redirect, url_for, flash, Response
from flask_restful import Resource, Api
from pymongo import MongoClient
import pymongo
import os
import csv
import flask
import json

from password import hash_password, verify_password
from testToken import generate_auth_token, verify_auth_token
from flask_wtf import Form, CSRFProtect
from wtforms import BooleanField, StringField,PasswordField
from wtforms.validators import DataRequired
from flask_login import (LoginManager, current_user, login_required,
                            login_user, logout_user, UserMixin,
                            confirm_login, fresh_login_required)

# Instantiate the app
app = Flask(__name__)
api = Api(app)
client = MongoClient(os.environ['DB_PORT_27017_TCP_ADDR'], 27017)

db = client.tododb
usersdb = client.users
app.config['SECRET_KEY'] = "yeah, not actually a secret"
DEBUG = True
login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "login"
login_manager.login_message = "Please log in to access this page."
login_manager.refresh_view = "reauth"

@login_manager.user_loader
def load_user(user_id):
    
    user = str(user_id)
    users = usersdb.users.find_one(user)
    if users == '' or users == None:
        return None
    return User(users)

class User():
    def __init__(self, user_id):
        self.user_id = user_id
    def is_authenticated(self):
        return True
    def is_active(self):
        return True
    def is_anonymous(self):
        return False
    def get_id(self):
        return str(self.user_id)

class RegisterationForm(Form):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])

class LoginForm(Form):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    remember = BooleanField('remember')
    
@app.route('/api/register', methods=['GET','POST'])
def register():

        form = RegisterationForm()
        username = request.form.get('username')
        password = request.form.get('password')
        
        if request.method == 'POST' and form.validate():
            user = usersdb.users.find_one({'username': username})

            if user == None:
                #hash the password then get rid of password
                hVal = hash_password(password)
                password = ''
                
                addUser = {'username':username, 'password':hVal}
                #adds new user to database
                addedUser = usersdb.users.insert_one(addUser)
                user_id = str(addedUser.inserted_id)
                return jsonify({'username':addUser['username'],'location':user_id}), 201
            else:
                flash("User already exists, please try a different username"),400
        
        return render_template('register.html',form=form), 400


@app.route('/api/token', methods=['GET','POST'])
def login():

    form = LoginForm()
    username = request.form.get('username')
    password = request.form.get('password')
    #remember showed y or none, bool forces it to be true or false
    remember = bool(request.form.get('remember'))
    app.logger.debug(remember)

    if (request.method == 'POST' or request.method == 'GET') and form.validate():
        user = usersdb.users.find_one({'username': form.username.data})
                    
        if user != None and verify_password(password,user['password']):
            
            login_user(User(user),remember=remember)
            token = generate_auth_token()
            decoded = token.decode()
            return jsonify({'token': decoded, 'duration': 600}), 201

        else:
            flash("username or password is invalid"), 400
                
    return render_template('login.html', form=form)

@login_required
@app.route('/logout')
def logout():
    
    logout_user()
    return 'Logged out successfully',200

@app.route('/')
def index():
    return render_template('index.html'),200

#proj6's part
class list_all(Resource):

#    @login_required
    def get(self):

        openT = []
        closeT = []
        #check if token was given, then verify
        token = request.args.get('token')
        if token == None:
            return "ERROR 401: Failed to locate token", 401
        if not verify_auth_token(token):
            return "ERROR 401: Failed to authenticate, check validity or token is expired", 401

        temp = request.args.get('top')
        if temp != None:
            top = int(temp)
            _items = db.tododb.find().limit(top)
        else:
            _items = db.tododb.find()

        items = [item for item in _items]
        
        for i in items:
            openT.append(i['opening'])
            closeT.append(i['closing'])

        results = {'opening':openT, 'closing':closeT}

        return results


class openOnly_json(Resource):
    def get(self):
        openT = []
        temp = request.args.get('top')

        token = request.args.get('token')
        if token == None:
            return "ERROR 401: Failed to locate token", 401
        if not verify_auth_token(token):
            return "ERROR 401: Failed to authenticate, check validity or token has expired", 401

        if temp != None:
            top = int(temp)
            _items = db.tododb.find().limit(top)
        else:
            _items = db.tododb.find()

        items = [item for item in _items]

        for i in items:
            openT.append(i['opening'])
        results = {'open_times':openT}
        return results

class closeOnly_json(Resource):
    def get(self):

        token = request.args.get('token')
        if token == None:
            return "ERROR 401: Failed to locate token", 401
        if not verify_auth_token(token):
            return "ERROR 401: Failed to authenticate, check validity or token has expired", 401

        closeT = []
        temp = request.args.get('top')
        if temp != None:
            top = int(temp)
            _items = db.tododb.find().limit(top)
        else:
            _items = db.tododb.find()

        items = [item for item in _items]

        for i in items:
            closeT.append(i['closing'])

        results = {'close_times':closeT}
        return results

class list_all_csv(Resource):
    def get(self):
        
        token = request.args.get('token')
        if token == None:
            return "ERROR 401: Failed to locate token", 401
        if not verify_auth_token(token):
            return "ERROR 401: Failed to authenticate, check validity or token has expired", 401

        fileI = open('list.csv', 'w')
        fileO = csv.writer(fileI)
        temp = request.args.get('top')

        if temp != None:
            top = int(temp)
            _items = db.tododb.find().limit(top)

        else:
            _items = db.tododb.find()

        items = [item for item in _items]
        fileO.writerow(['km\t'+'Open Time\t'+ 'Close Time'])
        for i in items:
            fileO.writerow([i['kming']+ '\t' + i['opening'] + '\t' + i['closing']])

        fileR = open('list.csv', 'r')
        return Response(fileR, mimetype='text/csv' )

class openOnly_csv(Resource):
    def get(self):
        
        token = request.args.get('token')
        if token == None:
            return "ERROR 401: Failed to locate token", 401
        if not verify_auth_token(token):
            return "ERROR 401: Failed to authenticate, check validity or token has expired", 401

        fileI = open('list.csv', 'w')
        fileO = csv.writer(fileI)
        temp = request.args.get('top')

        if temp != None:
            top = int(temp)
            _items = db.tododb.find().limit(top)

        else:
            _items = db.tododb.find()

        items = [item for item in _items]
        fileO.writerow(['km\t'+'Open Time\t'])
        for i in items:
            fileO.writerow([i['kming']+ '\t' + i['opening']])

        fileR = open('list.csv', 'r')
        return Response(fileR, mimetype='text/csv' )

class closeOnly_csv(Resource):
    def get(self):
        
        token = request.args.get('token')
        if token == None:
            return "ERROR 401: Failed to locate token", 401
        if not verify_auth_token(token):
            return "ERROR 401: Failed to authenticate, check validity or token has expired", 401

        fileI = open('list.csv', 'w')
        fileO = csv.writer(fileI)
        temp = request.args.get('top')

        if temp != None:
            top = int(temp)
            _items = db.tododb.find().limit(top)

        else:
            _items = db.tododb.find()

        items = [item for item in _items]
        fileO.writerow(['km\t'+ 'Close Time'])
        for i in items:
            fileO.writerow([i['kming']+ '\t' + i['closing']])

        fileR = open('list.csv', 'r')
        return Response(fileR, mimetype='text/csv' )

api.add_resource(openOnly_json, '/listOpenOnly','/listOpenOnly/json')
api.add_resource(list_all, '/listAll','/listAll/json')
api.add_resource(closeOnly_json, '/listCloseOnly','/listCloseOnly/json')
api.add_resource(list_all_csv, '/listAll/csv')
api.add_resource(openOnly_csv,'/listOpenOnly/csv')
api.add_resource(closeOnly_csv,'/listCloseOnly/csv')


# Run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
