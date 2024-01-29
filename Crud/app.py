from flask import Flask, url_for, redirect,session,request, g
from flask.templating import render_template
from database import get_database
from werkzeug.security import generate_password_hash, check_password_hash
import os 
import sqlite3

app=Flask(__name__)
app.config['SECRET_KEY'] = os.random(24)

@app.teardown_appcontext
def close_database(error):
    if hasattr(g, 'crudapplication_db'):
        g.crudapplication_db.close()


def get_current_user():
    user=None
    if 'user' in session:
        user = session['user']
        db=get_database()
        user_cur=db.execute('select * from users where name =?', [user])
        user = user_cur.fetchone()

    return user 

@app.route('/')
def index():
    user = get_current_user()
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    user = get_current_user()
    error = None
    db = get_database()
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        user_cur = db.execute('select * from users where name = ?', [name])
        user = user_cur.fetchone()
        if user:
            if check_password_hash(user['password'], password=password):
                session['user'] = user['name']
                return redirect(url_for('dashboard'))
            else:
                error = "Username or password did not match."
        else:
            error = "Username or password did not match."

    return render_template('login.html', loginerror=error, user=user)

@app.route('/register', methods=['GET', 'POST'])
def register():
    user = get_current_user()
    db = get_database()
    error = None
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        hash_password = generate_password_hash(password=password)
        existing_username = db.execute('select * from users where name = ?', [name]).fetchone()
        if existing_username:
            return redirect(url_for('register', registererror='Username already exists'))
        db.execute('insert into users (name, password) values (?, ?)', [name, hash_password])
        db.commit()
        return redirect(url_for('home'))

    return render_template('register.html', user=user)


@app.route('/dashboard', methods=["POST","GET"])
def dashboard():
    user = get_current_user()
    db = get_database()
    if request.method == "GET":
        emp_cur = db.execute('select * from emp')
        allemp = emp_cur.fetchall()
        #return redirect(url_for('dashboard', allemp=allemp, user=user))

    return render_template('dashboard.html', user = user, allemp=allemp )

@app.route('/addnewemployee', methods=["POST","GET"])
def addnewemployee():
    user = get_current_user()
    if request.method=="POST":
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        db = get_database()
        db.execute('insert into emp(name,email,phone,address) values(?,?,?,?)',[name,email,phone,address])
        db.commit()
        return redirect(url_for('dashboard'))
    return render_template('addnewemployee.html',user = user )

@app.route('/singleemployee/<int:empid>')
def singleemployeeprofile(empid):
    user = get_current_user()
    db = get_database()
    emp_cur=db.execute('select * from emp where empid = ?', [empid])
    single_emp=emp_cur.fetchone()
    return render_template('singleemployeeprofile.html', user = user, single_emp=single_emp )



@app.route('/fetchone/<int:empid>')
def fetchone(empid):
    user=get_current_user()
    db = get_database()
    emp_cur = db.execute('select * from emp where empid=?',[empid])
    single_emp=emp_cur.fetchone()
    return render_template('updateemployee.html',user=user, single_emp=single_emp)


@app.route('/updateemployee', methods=["POST","GET"])
def updateemployee():
    user = get_current_user()
    if request.method=="POST":
        empid=request.form['empid']
        name=request.form['name']
        email=request.form['email']
        phone = request.form['phone']
        address=request.form['address']
        db=get_database()
        db.execute('update emp set name=?, email=?, phone=?, address=? where empid=?',[name,email,phone,address,empid])
        db.commit()
        return redirect(url_for('dashboard',user=user))
    return render_template('updateemployee.html', user = user )

@app.route('/deleteemp/<int:empid>',methods=["GET","POST"])
def deleteemp(empid):
    user = get_current_user()
    if request.method=='GET':
        db=get_database()
        db.execute('delete from emp where empid=?',[empid])
        db.commit()
        return redirect(url_for('dashboard'))
    return render_template('dashboard.html',user=user)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return render_template('home.html')


if __name__=='__main__':
    app.run(debug=True)