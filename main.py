from flask import Flask,render_template,request,redirect,url_for,flash,session
import os
from livereload import server
from database2 import get_driver_kpis,get_driver_profile,get_driver_trip_history,total_revenue,total_dispatches,active_trips,completed_trips,net_profit,expense_against_revenue,month_revenue,monthly_expense,invoice_table,payments_table,check_user,get_specific_driver,get_customer_details,get_customer_shipments,shipments_per_customer,sidebar_logs
from flask_bcrypt import bcrypt
app=app=Flask(__name__)
app.secret_key=os.urandom(24)
@app.route('/')
def homepage():
    return render_template('index.html')
    
@app.route('/login',methods=['POST','GET'])
def login():
    if request.method=='POST':
        possible_email=request.form['email']
        possible_password=request.form['password']
        user=check_user(possible_email)
        if not user:
            flash('Non-registered user, Please register','danger')
            return redirect(url_for('login'))
        else:
            if possible_password==user[2]:
                if user[3]=='admin':
                    return redirect(url_for('analytics'))
                elif user[3]=='driver':
                    driver_login=get_specific_driver(user[0])
                    session['driver_id']=driver_login[0]
                    return redirect(url_for('drivers'))
                elif user[3]=='customer':
                    customer_login=get_customer_details(user[0])
                    session['customer_id']=user[0]
                    return redirect(url_for('customers'))
                else:
                    flash('No Role Assigned,Check With Admin','warning')

            else:
                flash('Incorrect password, Try Again','warning')
                return redirect(url_for('login'))


    return render_template('login.html')



@app.route('/customers')
def customers():
    account_id = session.get('customer_id')
    
    if not account_id:
        flash('Please log in to access this page.', 'danger')
        return redirect(url_for('login'))
    customer_details = get_customer_details(account_id)
    
    if not customer_details:
        flash (f"Could not find a customer profile matching User ID {account_id}.",'danger')
    customer_id         = customer_details[0]
    user_id             = customer_details[1]
    customer_email      = customer_details[2]
    customer_name       = customer_details[3] 
    account_status      = customer_details[4]
    shipments_ordered=get_customer_shipments(customer_id)
    listed_shipments=shipments_per_customer(customer_id)
    sidebar=sidebar_logs(customer_id)

    return render_template('customers.html',
                           account_status=account_status,
                           shipments_ordered=shipments_ordered[0],
                           customer_email=customer_email,
                           customer_name=customer_name,
                           listed_shipments=listed_shipments,
                           sidebar=sidebar
                           )



@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')




@app.route('/drivers')
def drivers():

    test_driver_id = session.get('driver_id')
    
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
    m_expense=monthly_expense()
    m_revenue=month_revenue()
    table_invoice_data=invoice_table()
    invoice_data=invoice_table()
    payments_data=payments_table()


    return render_template(
        'analytics.html',
        totalrevenue=totalrevenue,
        totaldispatches=totaldispatches[0],
        completedtrips=comletedtrips[0],
        netprofit=netprofit[4],
        m_expense=m_expense,
        m_revenue=m_revenue,
        operational_months=[str(i[0]) for i in (expense_against_revenue())],
        invoice_data=invoice_data,
        payments_data=payments_data

        )


@app.route('/maintenance')
def maintenance():
    return render_template('maintenance.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Logged Out Successfully', 'success')
    return redirect(url_for('login'))


app.run(debug=True)
server=app.wsgi_app
server.watch('static/')
server.watch('templates/')
