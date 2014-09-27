
from flask import Flask, session, redirect, url_for, escape, request, g, render_template
import sqlite3
import re
import hashlib
import binascii

app = Flask(__name__)

GET_HELP = 'get_help'
HELP = 'help'

DATABASE = './flaskr.db'

class Match(object):
    full_name = None
    email = None
    photo = None

    def __init__(self, full_name, email, photo=None):
        self.full_name = full_name
        self.email = email
        self.photo = photo

class Catch(object):
    full_name = None
    email = None
    photo = None
    course = None
    description = None
    timestamp = None

    def __init__(self, attribute_array):
        self.full_name = attribute_array[0]
        self.email = attribute_array[1]
        # self.photo = photo
        self.course = attribute_array[2]
        self.offer = attribute_array[3]
        self.timestamp = attribute_array[4]
        self.location = attribute_array[5]
        # self.description = description

def connect_db():
    return sqlite3.connect(DATABASE)


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()

@app.route('/',  methods=['GET','POST'])
def index():
    error = None
    full_name = None
    #handles the index form being submitted
    if request.method == 'POST':
        #handle logging in through the navbar
        if request.form['submit'] == 'nav_login':
            if login(request.form['nav_email'], request.form['nav_password']):
                full_name = session['full_name']
            else:
                error = 'Incorrect username or password'

        #handle the case where it's someone asking for help
        elif request.form['submit'] == GET_HELP:
            session['state'] = GET_HELP
            session['course'] = request.form['course']
            #TODO: do we want to split locations into an array here?
            session['locations'] = request.form['locations']
            #TODO: add in description functionality
            #session['description'] = request.form['description']
            session['offer'] = request.form['offer']

        #handle the case where it's someone wanting to help
        #elif request.form['submit'] == 'HELP'
        else:
            session['state'] = HELP
            session['expert_courses'] = request.form['expert_courses']

        #if user is already logged in
        if 'userID' in session:
            if session['state'] == GET_HELP:
                return redirect(url_for('my_matches'))
            else:
                return redirect(url_for('my_catches'))

        else:
            return redirect(url_for('login_register'))

    #display the html template
    return render_template('test_index.html', full_name=full_name, error=error)


@app.route('/user/my_matches')
def my_matches():
    # session['course'] is course requested help
    session['course'] = 2
    matches = g.db.execute('select userID from userCourses where courseID = ?', [session['course']])
    match_obj_array = []
    for id in matches:
        user_attributes = g.db.execute('select fullName, userName from users where id = ?', id)
        user_attributes_fetch = user_attributes.fetchone()
        match_obj_array.append(Match(user_attributes_fetch[0], user_attributes_fetch[1]))
    #return str(match_obj_array)
    return render_template('test_matches.html', matches=match_obj_array)

@app.route('/user/my_catches')
def my_catches():
    session['course'] = 1
    catches = g.db.execute('select id from requests where courseID = ?', [session['course']])
    catch_obj_array = []
    for id in catches:
        request_attributes = g.db.execute('select fullName, userName, code, offer, unixTime, location from requests inner join users on users.id = requests.userID inner join courses on courses.id = requests.courseID')
        request_attributes_fetch = request_attributes.fetchone()
        catch_obj_array.append(Catch(request_attributes_fetch))
    return render_template('test_catches.html', catches=catch_obj_array)


'''now a helper function that takes a email and password, checks if valid against the db,
sets the session user ID if so, and then returns true/false'''
def login(email, password):
    hashed_pass = hashlib.sha2242(password).hexdigest()
    user = g.db.execute('select id, fullName from users where userName = ? and hashedPass = ?', email, hashed_pass)
    if user:
        session['userID'] = user.fetchone()[0]
        session['full_name'] = user.fetchone()[1]
    else:
        return False


'''now a helper function that takes the registration form info, checks if valid against the db,
sets the session email if so, and then returns true/false'''
def register(full_name, email, password1, password2):
    re1 = '((?:[a-z][a-z]+))'  # Word 1
    re2 = '(\\d+)'  # Integer Number 1
    re3 = '(@)'  # Any Single Character 1
    re4 = '(cornell\\.edu)'	 # Fully Qualified Domain Name 1

    rg = re.compile(re1+re2+re3+re4, re.IGNORECASE|re.DOTALL)
    m = rg.search(email)

    existing_user = g.db.execute('select userName from users where userName = ?', email);
    if existing_user:
        return False
    elif password1 != password2:
        return False
    elif not m:
        return False
    else:
        hashed_pass = hashlib.sha224(password1).hexdigest()
        g.db.execute("INSERT INTO users (userName,hashedPass) VALUES (?,?)", email, hashed_pass)
        return True


@app.route('/loginregister', methods=['GET', 'POST'])
def login_register():
    error = None
    #handles the register or login form being submitted
    if request.method == 'POST':

        #if logging in
        if request.form['submit'] == 'login':
            if login(request.form['l_email'], request.form['l_password']):
                if session['state'] == GET_HELP:
                    redirect(url_for(my_matches))
                #elif session['state'] == HELP:
                else:
                    redirect(url_for(my_catches))
            else:
                error = 'Invalid email or password'

        #if registering
        #elif request.form['submit'] == 'register'"
        else:
            r_email = request.form['r_email']
            r_full_name = request.form['r_full_name']

            if register(r_full_name, r_email, request.form['r_password1'], request.form['r_password2']):

                #TODO:we should change this later to go to "waiting for confirmation" page
                if session['state'] == GET_HELP:
                    redirect(url_for(my_matches))
                #elif session['state'] == HELP:
                else:
                    redirect(url_for(my_catches))
            else:
                error = 'Invalid email or password'

    #else if there's no post information
    return render_template('test_loginregister.html', error=error)


@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('index'))

# set the secret key.  keep this really secret:
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

if __name__ == '__main__':
    app.run(debug=True)
