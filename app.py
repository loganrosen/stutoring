from flask import Flask, session, redirect, url_for, escape, request

app = Flask(__name__)

@app.route('/')
def index():
    #handles the index form being submitted
    if request.method == 'POST':

        #handle the case where it's someone asking for help
        #TODO: this might not work, test with the prototype
        if request.form['submit'] == 'get_help':
            session['course'] = request.form['course']
            #TODO: do we want to split locations into an array here?
            session['locations'] = request.form['locations']
            session['description'] = request.form['description']
            session['offer'] = request.form['offer']

        #handle the case where it's someone wanting to help
        #elif request.form['submit'] == 'help'
        else:
            session['expert_courses'] = request.form['expert_courses']

        if 'username' in session:
            if request.form['submit'] == 'get_help':
                #TODO: url name subject to change
                return redirect(url_for('my_matches', username=session['username']))
            else:
                #TODO: url name subject to change
                return redirect(url_for('my_catches'))

        else:
            return redirect(url_for('login_or_register'))
    else:
        #display the html template
        pass

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('index'))
    return '''
        <form action="" method="post">
            <p><input type=text name=username>
            <p><input type=submit value=Login/Register>
        </form>
    '''
# route thingy (get or post
def register():
    #registers
    pass

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('index'))

# set the secret key.  keep this really secret:
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

if __name__ == '__main__':
    app.run(debug=True)
