
from flask import Flask, session, redirect, url_for, escape, request, g, render_template
import sqlite3, re, hashlib, binascii

app = Flask(__name__)

GET_HELP = 'get_help'
HELP = 'help'

DATABASE = './flaskr.db'

def connect_db():
    return sqlite3.connect(DATABASE)

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()

@app.route('/')
def index():

    error = None
    #handles the index form being submitted
    if request.method == 'POST':
        #handle logging in through the navbar
        if request.form['submit'] == 'nav_login':
            if login(request.form['nav_email'], request.form['nav_password']):
                #TODO: if it turns out there's no need for this, refactor to if not statement
                pass
            else:
                error = 'Incorrect username or password'

        #handle the case where it's someone asking for help
        #TODO: this might not work, test with the prototype
        elif request.form['submit'] == GET_HELP:
            session['state'] = GET_HELP
            session['course'] = request.form['course']
            #TODO: do we want to split locations into an array here?
            session['locations'] = request.form['locations']
            session['description'] = request.form['description']
            session['offer'] = request.form['offer']

        #handle the case where it's someone wanting to help
        #elif request.form['submit'] == 'HELP'
        else:
            session['state'] = HELP
            session['expert_courses'] = request.form['expert_courses']

        #if user is already logged in
        if 'email' in session:
            if session['state'] == GET_HELP:
                return redirect(url_for('my_matches'))
            else:
                return redirect(url_for('my_catches'))

        else:
            return redirect(url_for('login_register'))

    #display the html template
    return render_template('index.html', logged_in=session['full_name'], error=error)


@app.route('/user/my_matches')
def my_matches():
    # session['course'] is course requested help
    matches = g.db.execute('select userID from userCourses where courseID = ?', [session['course']]);


@app.route('/user/my_catches')
def my_catches():
    catches = g.db.execute('select id from requests where courseID = ?', [session['course']]);


'''now a helper function that takes a email and password, checks if valid against the db,
sets the session user ID if so, and then returns true/false'''
def login(email, password):
    hashedPass = hashlib.sha2242(password1).hexdigest()
    user = g.db.execute('select id from users where userName = ? and hashedPass = ?', email, hashed_pass);
    if user:
        session['userID'] = user
    else:
        return false


'''now a helper function that takes the registration form info, checks if valid against the db,
sets the session email if so, and then returns true/false'''
def register(email, password1, password2):
    existing_user = g.db.execute('select userName from users where userName = ?', email)
    if existing_user:
        return false
    elif password1 != password2:
        return false
    elif not re.match(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}\b", email):
        return false
    else:
        hashed_pass = hashlib.sha224(password1).hexdigest()
        g.db.execute("INSERT INTO users (userName,hashedPass) VALUES (?,?)", email, hashed_pass)
        return true


@app.route('/loginregister', methods=['GET', 'POST'])
def login_register():
    error = None
    #handles the register or login form being submitted
    if request.method =='POST':

        #if logging in
        #TODO: this might not work, test
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
    return render_template('loginregister.html', error=error)


'''@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('index'))
    return
        <form action="" method="post">
            <p><input type=text name=username>
            <p><input type=submit value=Login/Register>
        </form>

'''
# route thingy (get or post
'''def register():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('index'))
    return
        <form action="" method="post">
        <p><input type=text name=username>
        <p><input type=submit value=Login/Register>
        </form>

    #registers
    pass
'''

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('index'))

# set the secret key.  keep this really secret:
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

if __name__ == '__main__':
    app.run(debug=True)
