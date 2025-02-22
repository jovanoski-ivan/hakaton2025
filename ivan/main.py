from flask import Flask, render_template, request, redirect, session, jsonify
import json
import datetime

#flask app
app = Flask(__name__)

app.secret_key = "BAD_SECRET_KEY"

#test data

db_name = "db.json"

#get users
#Modify
def get_users():
    with open(db_name, 'r') as user_db:
        users = json.load(user_db)

    return users['users']

#add users
#Modify
def add_user(email, username, password):
    new_user = {"username" : username, "email" : email, "password" : password, "followers" : 0}

    with open(db_name, 'r+') as user_db:
        user_data = json.load(user_db)
        user_data['users'].append(new_user)
        user_db.seek(0)
        json.dump(user_data, user_db, indent=4)

def get_posts():
    with open(db_name, 'r') as user_db:
        users = json.load(user_db)

    return users['posts']

def create_post(title, description):
    current_date = datetime.datetime.now()

    # Format the date as DD/MM/YYYY
    formatted_date = current_date.strftime('%d/%m/%Y')
    new_post = {"description":description, "title": title, "author":session['username'], "date":formatted_date}

    with open(db_name, 'r+') as post_db:
        post_data = json.load(post_db)
        post_data['posts'].append(new_post)
        post_db.seek(0)
        json.dump(post_data, post_db, indent=4)

#---------------
        


@app.route("/")
def index():
    if 'username' not in session:
        session['username'] = None

    if not session['username']:
        return jsonify({"session":0, "posts":get_posts()})
    

    
    return jsonify({"session":1, "username":session['username'], "posts":get_posts()})


@app.route('/posts')
def posts():
    return jsonify(get_posts())



@app.route("/login", methods=['GET', 'POST'])
def login():

    if 'username' not in session:
        session['username'] = None

    if session['username']:
        return jsonify({"code":-1})
    
    if request.method=='POST':

        data = request.get_json()

        #check if login form is valid
        if not data['username'] or not data['password']:
            return jsonify({"code" : -1})
        
        users = get_users()
        
        #check if info is valid
        for user in users:
            if data['username'] == user['username']:
                if data['password'] == user['password']:
                    session['username'] = user['username']
                    return jsonify({"username":user['username']})
        
        return jsonify({"code" : -1})
    
    return render_template("login.html")

@app.route('/logout', methods=['POST'])
def logout():
    if session['username']:
        session.pop('username', None)
        return jsonify({"code": 1})
    
    return jsonify({"code":-1})



@app.route('/register', methods=['GET', 'POST'])
def register():

    data = request.get_json()

    if 'username' not in session:
        session['username'] = None

    if session['username']:
        return jsonify({"code":-1})

    if request.method == 'POST':
        if not data['username'] or not data['password'] or not data['email']:
            return jsonify({"Error" : "Can't register user"})
        
        for user in get_users():
            if user['username'] == data['username'] or user['email'] == data['email']:
                return jsonify({"Error" : "User already exists"})
        
        add_user(data['email'], data['username'], data['password'])
        session['username'] = data['username']
        return redirect('/')
    
    return render_template('register.html')



@app.route('/add_post', methods=['POST'])
def add_post():
    if 'username' not in session:
        session['username'] = None

    if not session['username']:
        return jsonify({"code":-1}) 
    
    data = request.get_json()

    if not data['title'] or not data['description']:
        return jsonify({"code":-1})
    
    create_post(data['title'], data['description'])

    return jsonify({"code":1})
     

#run app locally
app.run(host="0.0.0.0", port="80")