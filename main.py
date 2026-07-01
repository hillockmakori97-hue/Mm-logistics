from flask import Flask,render_template,request
import os
from livereload import server
S_key=os.urandom(24)
app=app=Flask(__name__)
@app.route('/')
def homepage():
    return render_template('customers.html')

@app.route('/customers')
def customers():
    return render_template('customers.html')
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')
@app.route('/drivers')
def drivers():
    
    return render_template('drivers.html')
@app.route('/services')
def services():
    return render_template('services.html')
@app.route('/trucks')
def trucks():
    return render_template('trucks.html')
@app.route('/analytics')
def analytics():
    return render_template('analytics.html')
@app.route('/login')
def login():
    return render_template('login.html')
@app.route('/maintenance')
def maintenance():
    return render_template('maintenance.html')

app.run(debug=True)
server=app.wsgi_app
server.watch('static/')
server.watch('templates/')