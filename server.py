from flask import Flask, render_template, session, redirect, request, flash
import re #importing the regex module
from flask_bcrypt import Bcrypt
from mysqlconnection import connectToMySQL

app = Flask(__name__, template_folder="templates")
app.secret_key = "secretkey"
bcrypt = Bcrypt(app)

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
BIRTHDAY_REGEX = re.compile(r'^(19|20)\d\d[- /.](0[1-9]|1[012])[- /.](0[1-9]|[12][0-9]|3[01])$')

def login_user(user_info, session_object):
    session_object['curr_user_id'] = user_info['id']
    session_object['curr_user_name'] = user_info['name']

@app.route('/')
def show_login():
    print("*"*80)
    print("in the show_login function")
    return render_template ("login.html")

@app.route('/home')
def show_home():
    print("*"*80)
    print("in the show_home function")
    if not 'curr_user_id' in session:
        return redirect("/")
    else:
        # get logged in user data
        logged_in_user = {
            'name': session['curr_user_name'],
            'id': session['curr_user_id']
        }
        print(logged_in_user)
        print(logged_in_user['id'])
        print("*"*50)

        mysql = connectToMySQL("trips")
        travel_query = "SELECT * FROM users JOIN trips ON trips.user_id = users.id WHERE users.id = %(user_id)s;"
        data= {
            'user_id': session['curr_user_id'],
        }
        trips = mysql.query_db(travel_query, data)
        print(trips)
        context2 = {
            'trips' : trips,
        }
        # get all users
        mysql = connectToMySQL("trips")
        users_query = "SELECT * FROM users;"
        users = mysql.query_db(users_query)
        print(users)
        context = {
            'user': logged_in_user,
            'users': users,
        }
        return render_template("home.html", context=context, context2 = context2)

@app.route('/create_trip')
def show_create_trip():
    print("*"*80)
    print("in the show_create_trip function")
    if not 'curr_user_id' in session:
        return redirect("/")

    logged_in_user = {
        'name': session['curr_user_name'],
        'id': session['curr_user_id']
    }
    print(logged_in_user)
    print(logged_in_user['id'])
    print("*"*50)

    mysql = connectToMySQL("trips")
    users_query = "SELECT * FROM users;"
    users = mysql.query_db(users_query)
    print(users)
    context = {
        'user': logged_in_user,
        'users': users,
    }
    return render_template ("create_trip.html", context=context)

@app.route('/edit_trip/<trip_id>')
def show_edit_trip(trip_id):
    print("*"*80)
    print("in the show_edit_trip function")
    if not 'curr_user_id' in session:
        return redirect("/")

    logged_in_user = {
        'name': session['curr_user_name'],
        'id': session['curr_user_id']
    }
    print(logged_in_user)
    print(logged_in_user['id'])

    mysql = connectToMySQL("trips")
    users_query = "SELECT * FROM users;"
    users = mysql.query_db(users_query)
    print(users)
    context = {
        'user': logged_in_user,
        'users': users,
    }

    mysql = connectToMySQL("trips")
    query = "SELECT * FROM trips WHERE trip_id = %(trip)s;"
    data = {
        'trip': trip_id
    }
    trip = mysql.query_db(query, data)
    return render_template ("edit_trip.html", trip=trip, context=context)

@app.route('/trip_details/<trip_id>')
def show_trip_details(trip_id):
    # can pass the trip_id value in the url through jinja in html
    print("*"*80)
    print("in the show_trip_details function")
    if not 'curr_user_id' in session:
        return redirect("/")

    # allows access to stored session variables, in this case name and id
    logged_in_user = {
        'name': session['curr_user_name'],
        'id': session['curr_user_id']
    }
    print(logged_in_user)
    print(logged_in_user['id'])

    # SQL query to obtain details of the trip from the trips table
    mysql = connectToMySQL("trips")
    travel_query = "SELECT * FROM trips WHERE trip_id = %(trip_id)s;"
    # the WHERE clause allows the query to return a more specific set of data, in this case the trip info. for that specific destination
    data = {
        'trip_id': trip_id,
    }
    trips = mysql.query_db(travel_query, data)
    print(trips)
    context2 = {
        'trips' : trips,
    }

    mysql = connectToMySQL("trips")
    query2 = "SELECT users.first_name FROM users JOIN trips ON trips.user_id = users.id WHERE trip_id = %(trip_id)s;"
    data1 = {
        'trip_id': trip_id,
    }
    trips2 = mysql.query_db(query2, data1)
    print(trips2)
    context3 = {
        'trips2' : trips2,
    }

    mysql = connectToMySQL("trips")
    users_query = "SELECT first_name FROM users;"
    users = mysql.query_db(users_query)
    print(users)
    context = {
        'user': logged_in_user,
        'users': users,
    }
    return render_template("trip_details.html", context2=context2, context=context, context3=context3)

@app.route('/logout')
def logout():
    print("*"*80)
    print("logging out")
    session.clear()
    return redirect("/")

@app.route("/register", methods=["POST"])
def register():
    print("*"*80)
    print(request.form)
    error_messages = []
    # check validations
    if not request.form['first_name'].isalpha(): #returns a boolean that shows whether a string contains only alphabetic characters
        error_messages.append("First name must be alphabetic characters!")
    if len(request.form['first_name']) < 2:
        error_messages.append("First name must be longer than two characters!")
    if len(request.form['last_name']) < 2:
        error_messages.append("Last name needs to be longer than two characters!")
    if not EMAIL_REGEX.match(request.form['email']): #test whether a field matches the email pattern
        error_messages.append("Email must follow format name@email.com")
    if request.form['password'] != request.form['confirm_password']:
        error_messages.append("Passwords don't match")
    if len(request.form['confirm_password']) < 2:
        error_messages.append("Passwords don't match")
    if len(request.form['password']) < 2:
        error_messages.append("Password must be longer than two characters")

    if len(error_messages) == 0:
        # log our user in...
        pw_hash = bcrypt.generate_password_hash(request.form['password']) #creates a password hash
        mysql = connectToMySQL("trips")
        query = "INSERT INTO users (first_name, last_name, email, password_hash, created_at, updated_at) VALUES (%(first)s, %(last)s, %(email)s, %(password)s, NOW(), NOW());"
        data = {
            'first': request.form['first_name'],
            'last': request.form['last_name'],
            'email': request.form['email'],
            'password': pw_hash,
        }
        results = mysql.query_db(query, data)
        print(results)
        login_user({'id': results, 'name': request.form['first_name']}, session)
        return redirect("/home")
    else:
        # flash a bunch of messages
        for message in error_messages:
            print(message)
            flash(message)
        return redirect("/")

@app.route("/login", methods= ['POST'])
def login():
    errors = []
    # grab deetz
    input_pw = request.form['password']
    input_email = request.form['email']
    # see if user exists
    mysql = connectToMySQL("trips")
    query = "SELECT * FROM users WHERE(email = %(email)s)"
    data = {
        'email': input_email
    }
    result = mysql.query_db(query, data)
    if len(result) is not 1:
        errors.append("Email is incorrect!")
    else:
        if not bcrypt.check_password_hash(result[0]['password_hash'], input_pw):
            errors.append("Password is incorrect!")
        else:
            login_user({'id': result[0]['id'], 'name':result[0]['first_name']}, session)
            print(session)
    if len(errors) == 0:
        return redirect("/home")
    else:
        flash("Incorrect login")
        return redirect("/")

@app.route("/trip/new", methods=["POST"])
def new_trip():
    print("*"*80)
    print("in new_trip function")
    print(request.form)
    error_messages = []
    # check validations
    if len(request.form['destination']) < 3:
        error_messages.append("Destination must be at least three characters long!")
    if len(request.form['plan']) < 3:
        error_messages.append("Plan must be at least three characters long!")
    if len(request.form['start_date']) < 1:
        error_messages.append("Must include a start date!")
    if len(request.form['end_date']) < 1:
        error_messages.append("Must include a end date!")
    # date validation BLACK BELT!!!

    if len(error_messages) == 0:
        logged_in_user = {
            'name': session['curr_user_name'],
            'id': session['curr_user_id']
        }
        mysql = connectToMySQL("trips")
        query = "INSERT INTO trips (destination, start_date, end_date, plan, created_at, updated_at, user_id) VALUES (%(dest)s, %(start)s, %(end)s, %(plan)s, NOW(), NOW(), %(user_id)s);"
        data ={
            'dest': request.form['destination'],
            'start': request.form['start_date'],
            'end': request.form['end_date'],
            'plan': request.form['plan'],
            'user_id' : session['curr_user_id'],
        }
        print(data)
        trip_results = mysql.query_db(query, data)
        print(trip_results)
        return redirect("/home")
    else:
        for message in error_messages:
            print(message)
            flash(message)
        return redirect("/create_trip")

@app.route("/trip/edit/<trip_id>", methods=["POST"])
def edit_trip(trip_id):
    print("*"*50)
    print(request.form)
    error_messages = []

    logged_in_user = {
        'name': session['curr_user_name'],
        'id': session['curr_user_id']
    }
    # check validations
    if len(request.form['destination']) < 3:
        error_messages.append("Destination must be at least three characters long!")
    if len(request.form['plan']) < 3:
        error_messages.append("Plan must be at least three characters long!")
    if len(request.form['start_date']) < 1:
        error_messages.append("Must include a start date!")
    if len(request.form['end_date']) < 1:
        error_messages.append("Must include a end date!")
    # date validation BLACK BELT!!!

    if len(error_messages) == 0:
        mysql = connectToMySQL("trips")
        query = "UPDATE trips SET destination = %(dest)s, start_date = %(start)s, end_date = %(end)s, plan = %(plan)s, user_id = %(user_id)s WHERE trip_id = %(trip_id)s;"
        data ={
            'user_id' : session['curr_user_id'],
            'trip_id': trip_id,
            'dest': request.form['destination'],
            'start': request.form['start_date'],
            'end': request.form['end_date'],
            'plan': request.form['plan'],
        }
        new_trip = mysql.query_db(query, data)
        print(new_trip)
        return redirect("/home")
    else:
        for message in error_messages:
            print(message)
            flash(message)
        return redirect("/edit_trip")

@app.route('/delete/<trip_id>', methods=['POST'])
def delete(trip_id):
    print("*"*80)
    print("in the show_trip_details function")
    if not 'curr_user_id' in session:
        return redirect("/")

    logged_in_user = {
        'name': session['curr_user_name'],
        'id': session['curr_user_id']
    }

    print(logged_in_user)
    print(logged_in_user['id'])
    print("*"*50)

    # mysql = connectToMySQL("trips")
    # travel_query = "SELECT trips.trip_id, trips.destination, trips.start_date, trips.end_date, trips.plan  FROM trips;"
    # trips = mysql.query_db(travel_query)
    # print(trips)

    mysql = connectToMySQL('trips')
    query = "DELETE FROM trips WHERE trip_id = %(trip_id)s;"
    data = {
        "trip_id" : trip_id,
    }
    delete_trip = mysql.query_db(query, data)
    print(delete_trip)
    return redirect('/home')

if __name__=="__main__":
    app.run(debug=True)
