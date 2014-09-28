
from flask import Flask, session, redirect, url_for, escape, request, g, render_template, jsonify
import sqlite3
import re
import hashlib
import binascii
import datetime
import time

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
    offer = None
    course = None
    description = None
    timestamp = None

    def __init__(self, attribute_array):
        self.full_name = attribute_array[0]
        self.email = attribute_array[1]
        # self.photo = photo
        self.offer = attribute_array[2]
        self.timestamp = datetime.datetime.fromtimestamp(int(attribute_array[3])).strftime('%Y-%m-%d %H:%M:%S')
        self.location = attribute_array[4]
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

@app.route('/',  methods=['GET', 'POST'])
def index():
    error = None
    full_name = None
    session['userID'] = 1
    #handles the index form being submitted
    if request.method == 'POST':
        #handle logging in through the navbar
        '''if request.form['submit'] == 'nav_login':
            if login(request.form['nav_email'], request.form['nav_password']):
                full_name = session['full_name']
            else:
                error = 'Incorrect username or password'''

        #handle the case where it's someone asking for help
        if 'usernoexistsubmit' in request.form or 'userexistssubmit' in request.form:
            if 'usernoexistsubmit' in request.form:
                user_name = request.form['email']
                hashed_pass = 'password'
                full_name = request.form['fullname']
                #login information
                g.db.execute("INSERT INTO users (userName, hashedPass, fullName) VALUES (?,?,?)",
                             [user_name, hashed_pass, full_name])
                g.db.commit()
                session['userID'] = g.db.execute('select id from users where userName = ?', (user_name,)).fetchone()[0]
            else:
                user_name = request.form['email']
                session['userID'] = g.db.execute('select id from users where userName = ?', (user_name,)).fetchone()[0]

            course = request.form['course']
            #TODO: do we want to split locations into an array here?
            location = request.form['location']
            offer = request.form['offer']
            user_id = session['userID']
            course_id = g.db.execute('select id from courses where code = ?', [course]).fetchone()[0]
            unix_time = int(time.time())
            g.db.execute("INSERT INTO requests (userID, courseID, unixTime, location, offer, description) VALUES (?,?,?,?,?,?)",
                         [user_id, course_id, unix_time, location, offer, 'no description yet'])
            g.db.commit()
            return redirect(url_for('get_matches'))

        #handle the case where it's someone wanting to help
        #elif request.form['submit'] == 'HELP'
        else:
            if 'wantusernoexistsubmit' in request.form:
                user_name = request.form['wantemail']
                hashed_pass = 'password'
                full_name = request.form['fullname']
                g.db.execute("INSERT INTO users (userName, hashedPass, fullName) VALUES (?,?,?)",
                             [user_name, hashed_pass, full_name])
                g.db.commit()
                session['userID'] = g.db.execute('select id from users where userName = ?', (user_name,)).fetchone()[0]
            else:
                user_name = request.form['wantemail']
                session['userID'] = g.db.execute('select id from users where userName = ?', (user_name,)).fetchone()[0]

            course = request.form['expert_course']
            user_id = session['userID']
            course_id = g.db.execute('select id from courses where code = ?', [course]).fetchone()[0]
            app.logger.debug(course_id)

            g.db.execute("INSERT INTO userCourses (userID, courseID) VALUES (?,?)", [user_id, int(course_id)])
            g.db.commit()
            return redirect(url_for('get_catches'))

        #if user is already logged in
        '''if 'userID' in session:
            if session['state'] == GET_HELP:
                return redirect(url_for('my_matches'))
            else:
                return redirect(url_for('my_catches'))

        else:
            return redirect(url_for('login_register'))'''

    #display the html template
    return render_template('test_index.html', full_name=full_name, error=error)


#check if user exists
@app.route('/_user_exists')
def json_user_exists():
    user_name = str(request.args.get('userName'))
    existing_user = True if g.db.execute('select userName from users where userName = ?', (user_name,)).fetchone() else False
    return jsonify(result=existing_user)


@app.route('/_login')
def json_login():
    email = request.args.get('userName')
    hashed_pass = hashlib.sha2242(request.args.get('password').hexdigest())
    user = g.db.execute('select id, fullName from users where userName = ? and hashedPass = ?', (email, hashed_pass)).fetchone()
    if user:
        session['userID'] = user[0]
        session['fullName'] = user[1]
        return jsonify(result=True)
    else:
        return jsonify(result=False)


@app.route('/my_catches')
def get_catches():
    #TODO: add logic to display pre-existing courses one is an expert in
    proficient_course = g.db.execute('select courseID from userCourses where userID = ?', [session['userID']]).fetchone()
    app.logger.error(proficient_course)

    #     course_ids = g.db.execute('select userName, fullName from users where user = ?', [session['userID']]).fetchall()

    # for course in courses:
    #     course_id = g.db.execute('select courseID from courses where course = ?', [course]).fetchone()
    #     catches.append(g.db.execute('select id from requests where courseID = ?', [course_id]).fetchall())
    # catch_obj_lst = []
    # for id in catches:
    catches = g.db.execute('select requests.id from requests inner join courses on courses.id = requests.courseID where courses.id = ?',[proficient_course[0]]).fetchall()

    catch_obj_list = []
    for catch in catches:
        id = catch[0]
        app.logger.debug(str(id))
        request_attributes_fetch = g.db.execute('select fullName, userName, offer, unixTime, location from requests inner join users on users.id = requests.userID where requests.id = ?',[id]).fetchone()
        catch_obj_list.append(Catch(request_attributes_fetch))
    return render_template('test_catches.html', catches=catch_obj_list)

@app.route('/my_matches')
def get_matches():
    matches = []

    # session['course'] = 1
    #if you just added a course
    # if 'course' in session:
    #     course_id = g.db.execute('select id from courses where code = ?', [session['course']]).fetchone()
    #     matches.append(g.db.execute('select userID from userCourses where courseID = ?', [course_id]).fetchall())

    #add all existing courses
    course_ids = g.db.execute('select courseID from requests where userID = ?', [session['userID']]).fetchall()
    # app.logger.debug(course_ids)
    for course_id in course_ids:
        app.logger.debug(course_id[0])
        matches.append(g.db.execute('select userID from userCourses where courseID = ?', [course_id[0]]).fetchall())

    match_obj_lst = []
    app.logger.debug(str(matches))
    for id in matches[0]:
        app.logger.debug(id)
        user_attributes_fetch = g.db.execute('select fullName, userName from users where id = ?', [id[0]]).fetchone()
        match_obj_lst.append(Match(user_attributes_fetch[0], user_attributes_fetch[1]))
    return render_template('test_matches.html', matches=match_obj_lst)


@app.route('/_register')
def json_register():
    full_name = request.args.get('fullName')
    email = request.args.get('email')
    password1 = request.args.get('password1')
    password2 = request.args.get('password2')
    re1 = '((?:[a-z][a-z]+))'  # Word 1
    re2 = '(\\d+)'  # Integer Number 1
    re3 = '(@)'  # Any Single Character 1
    re4 = '(cornell\\.edu)'	 # Fully Qualified Domain Name 1

    rg = re.compile(re1+re2+re3+re4, re.IGNORECASE|re.DOTALL)
    m = rg.search(email)
    existing_user = g.db.execute('select userName from users where userName = ?', [email]).fetchone()
    if existing_user:
        return jsonify(result=False, reason='Another user exists with the email')
    elif password1 != password2:
        return jsonify(result=False, reason='Password entries do not match')
    elif not m:
        return jsonify(result=False, reason='Invalid email')
    else:
        hashed_pass = hashlib.sha224(password1).hexdigest()
        g.db.execute("INSERT INTO users (userName,hashedPass) VALUES (?,?)", [email, hashed_pass])
        return jsonify(result=True)

@app.route('/_logout')
def json_logout():
    # remove the username from the session if it's there
    return jsonify(result=True)


'''@app.route('/loginregister', methods=['GET', 'POST'])
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
    return render_template('test_loginregister.html', error=error)'''


# set the secret key.  keep this really secret:
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

if __name__ == '__main__':
    app.run(debug=True)
