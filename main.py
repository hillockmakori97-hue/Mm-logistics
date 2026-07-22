from flask import Flask,render_template,request,redirect,url_for,flash,session
import os
from livereload import server
from database2 import get_driver_kpis,get_driver_profile,get_driver_trip_history,total_revenue,total_dispatches,active_trips,completed_trips,net_profit,expense_against_revenue,month_revenue,monthly_expense,invoice_table,payments_table,check_user,get_specific_driver,get_customer_details,get_customer_shipments,shipments_per_customer,sidebar_logs,all_destinations,get_dest_coords,get_categories,get_dest_name,get_truck,get_available_driver,get_truck_end_odo,get_dispatcher,insert_trip,insert_shipment
from helper_functions import calculate_haversine_distance,calculate_cost
# from flask_bcrypt import bcrypt
from datetime import datetime
import random
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



@app.route('/customers', methods=['POST','GET'])
def customers():
    account_id = session.get('customer_id')
    
    if not account_id:
        flash('Please log in to access this page.', 'danger')
        return redirect(url_for('login'))
    customer_details = get_customer_details(account_id)
    
    if not customer_details:
        flash (f"Could not find a customer profile matching User ID {account_id}.",'danger')
    customer_id         = customer_details[0]
    session['acc_id']=customer_details[0]
    user_id             = customer_details[1]
    customer_email      = customer_details[2]
    customer_name       = customer_details[3] 
    account_status      = customer_details[4]
    shipments_ordered=get_customer_shipments(customer_id)
    listed_shipments=shipments_per_customer(customer_id)
    sidebar=sidebar_logs(customer_id)
    destinations_data=all_destinations()
    categories=get_categories()
    cargo_type=None
    amount=None
    payment_method=None
    weight=None
    origin_id=None
    destination_id=None
    pick_up_location=None
    drop_off_location=None
    cost=0

    if request.method == 'POST':
        drop_off_location=request.form['drop_off_location']
        destination_id=int(request.form['drop_off_location'])
        origin_id=int(request.form['pick_up_location'])
        origin_coords=get_dest_coords(origin_id)
        destination_coords=get_dest_coords(destination_id)
        lat1=origin_coords[0]
        lon1=origin_coords[1]
        lat2=destination_coords[0]
        lon2=destination_coords[1]
        distance=calculate_haversine_distance(lat1,lon1,lat2,lon2)
        cargo_type=request.form['cargo_type']
        weight=float(request.form['weight'])
        cost=calculate_cost(cargo_type,distance,weight)
        session['cost']=cost
        session['payment_method']=payment_method
        origin_name=get_dest_name(origin_id)
        destination_name=get_dest_name(destination_id)
        session['origin_id']=origin_id
        shipment_details=(origin_name,destination_name,origin_id,weight,destination_id,cargo_type)
        session['shipment_details']=shipment_details
        
        
    return render_template('customers.html',
                           account_status=account_status,
                           shipments_ordered=shipments_ordered[0],
                           customer_email=customer_email,
                           customer_name=customer_name,
                           listed_shipments=listed_shipments,
                           sidebar=sidebar,
                           destinations_data=destinations_data,
                           categories=categories,
                           cargo_type=cargo_type,
                           amount=amount,
                           payment_method=payment_method,
                           cost=cost,
                           drop_off_location=drop_off_location
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
@app.route('/payments',methods=['POST','GET'])
def payments():
    if request.method=='POST':
        cost=session.get('cost')
        payment_method=request.form['payment_method']
        if not cost or cost==0:
          flash('Nothing To Pay here, Make Trip Request First','warning')
          return redirect(url_for('customers'))
        else:
            phone_number=request.form['acc_number']
            flash('Payment Received Successfully','success')
            trucks=get_truck('active')
            print(trucks)
            listed_trucks=[i[0] for i in trucks]
            print(listed_trucks)
            if not trucks:
                flash('All Trucks En-route,Your Shipment will be handled as soon as possible','info')
            else:
                selected_truck=random.choice(listed_trucks)
                available_driver=get_available_driver('completed')
                if not available_driver:
                    flash('No Availabe Driver, We Will Get To Your Shipment As Soon As Possible','info')
                else:
                    listed_driver=[i[0] for i in available_driver]
                    selected_driver=random.choice(listed_driver)
                    flash('Driver And Truck Assigned Successfully Trip Assignment In Process','success')
                
                if not selected_driver or not selected_truck:
                    pass
                else:
                    shipment_details=session.get('shipment_details')
                    driver_id=selected_driver
                    truck_id=selected_truck
                    origin_id=shipment_details[2]
                    origin=shipment_details[0]
                    destination=shipment_details[1]
                    odo_end=get_truck_end_odo(truck_id)
                    odo_start=odo_end[0]
                    cargo_type=shipment_details[5]
                    dispatched_by=get_dispatcher(origin_id)
                    weight=shipment_details[3]
                    destination_id=shipment_details[4]
                    values=[driver_id,truck_id,origin,destination,odo_start,dispatched_by]
                    print(odo_start)
                    print(dispatched_by)
                    print(origin)
                    print(destination)
                    print(driver_id)
                    print(truck_id)
                    trip_id=insert_trip(values)    
                    acc_id=session.get('acc_id')
            
                    
                    shipment_values=(acc_id,origin,destination,trip_id,cargo_type,weight,origin_id,destination_id)
                    shipment_id=insert_shipment(shipment_values)
                    print(shipment_id)
            session.pop('cost')
    return redirect(url_for('customers'))


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
