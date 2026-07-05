from flask import Flask,render_template,request
import os
from livereload import server
from database2 import get_driver_kpis,get_driver_profile,get_driver_trip_history,total_revenue,total_dispatches,active_trips,completed_trips,net_profit
app=app=Flask(__name__)
@app.route('/')
def homepage():
    return render_template('index.html')
S_key=os.urandom(24)
    

@app.route('/customers')
def customers():
    return render_template('customers.html')
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')
@app.route('/drivers')
def drivers():

    test_driver_id = 202
    
    driver_profile = get_driver_profile(test_driver_id)
    driver_kpis = get_driver_kpis(test_driver_id)
    trip_history = get_driver_trip_history(test_driver_id)
    
    if not driver_profile:
        return f"Driver with ID {test_driver_id} not found in the database. Add a driver first!", 404

    return render_template(
        'drivers.html', 
        profile=driver_profile, 
        kpis=driver_kpis, 
        trips=trip_history
    )
@app.route('/services')
def services():
    return render_template('services.html')
@app.route('/trucks')
def trucks():
    return render_template('trucks.html')
@app.route('/analytics')
def analytics():
    totalrevenue= total_revenue()
    totaldispatches=total_dispatches()
    comletedtrips=completed_trips()
    netprofit=net_profit()

    return render_template(
        'analytics.html',
        totalrevenue=totalrevenue,
        totaldispatches=totaldispatches[0],
        completedtrips=comletedtrips[0],
        netprofit=netprofit[4]

        )
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