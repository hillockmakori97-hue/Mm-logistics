from flask import Flask,render_template,request,redirect,url_for,flash,session,jsonify
import os
from livereload import server
from database2 import get_driver_kpis,get_driver_profile,get_driver_trip_history,total_revenue,total_dispatches,active_trips,completed_trips,net_profit,expense_against_revenue,month_revenue,monthly_expense,invoice_table,payments_table,check_user,get_specific_driver,get_customer_details,get_customer_shipments,shipments_per_customer,sidebar_logs,all_destinations,get_dest_coords,get_categories,get_dest_name,get_truck,get_available_driver,get_truck_end_odo,get_dispatcher,insert_trip,insert_shipment,insert_payment,all_trucks,insert_maintenance_log,sum_maintenance_logs,get_maintenence_logs,get_stations,insert_fuel_log,insert_customer,all_trips,all_shipments,get_dispatcher_info,get_station_assignment,get_shipments_handled,get_weight_handled,get_staff_id,listed_shipments,set_trip_completed,update_driver_status,update_truck_status,get_driver_and_truck_by_trip_id,get_weight
from helper_functions import calculate_haversine_distance,calculate_cost
from flask_bcrypt import Bcrypt
from datetime import datetime
import random
import string
from functools import wraps
from decimal import Decimal
app=Flask(__name__)
bcrypt=Bcrypt(app)
app.secret_key=os.urandom(24)

def admin_protected(function):
    @wraps(function)
    def n(*k,**n):
        if 'admin_id' not in session:
            flash('This page is admin protected,PLease Log In As Admin','info')
            return redirect (url_for('login'))
        return function(*k,**n)
    return n



def dispatcher_protected(function):
    @wraps(function)
    def n(*k,**n):
        if 'staff_id' not in session:
            flash('This page is for dispatchers,PLease Log In As Dispatcher','info')
            return redirect (url_for('login'))
        return function(*k,**n)
    return n

def driver_protected(driver_access):
    @wraps(driver_access)
    def t(*e,**r):
        if 'driver_id' not in session:
            flash('This Page Is for Drivers Please Log In As A Driver','info')
            return redirect (url_for('login'))
        return driver_access(*e,**r)
    return t
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
            if bcrypt.check_password_hash(user[2],possible_password):
                if user[3]=='admin':
                    session['admin_id']=user[0]
                    session['role']=user[3]
                    return redirect(url_for('analytics'))
                elif user[3]=='driver':
                    driver_login=get_specific_driver(user[0])
                    session['driver_id']=driver_login[0]
                    session['role']=user[3]
                    return redirect(url_for('drivers'))
                elif user[3]=='customer':
                    customer_login=get_customer_details(user[0])
                    session['customer_id']=user[0]
                    session['role']=user[3]
                    return redirect(url_for('customers'))
                elif user[3]=='dispatcher':
                    staff_id=get_staff_id(user[0])
                    session['staff_id']=staff_id
                    session['staff_email']=user[1]
                    
                    return redirect(url_for('dispatchers'))
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
    total_weight=get_weight(customer_id)
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
@driver_protected
def drivers():
    test_driver_id = session.get('driver_id')
    driver_profile = get_driver_profile(test_driver_id)
    driver_kpis = get_driver_kpis(test_driver_id)
    trip_history = get_driver_trip_history(test_driver_id)
    fuel_trucks=all_trucks()
    stations=get_stations()
    if not driver_profile:
        return f"Driver with ID {test_driver_id} not found in the database. Add a driver first!", 404
    return render_template(
        'drivers.html', 
        profile=driver_profile, 
        kpis=driver_kpis, 
        trips=trip_history,
        fuel_trucks=fuel_trucks,
        stations=stations
    )



@app.route('/maintenance_logs')
@admin_protected
def maintenance_logs():
    maintenance_logs=get_maintenence_logs()
    return render_template('services.html',maintenance_logs=maintenance_logs)


@app.route('/trucks')
@admin_protected
def trucks():
    truck_data=all_trucks()
    return render_template('trucks.html',truck_data=truck_data)



@app.route('/analytics')
@admin_protected
def analytics():
    totalrevenue= total_revenue()
    totaldispatches=total_dispatches()
    comletedtrips=completed_trips()
    maitenance_sum=Decimal(sum_maintenance_logs())
    print(maitenance_sum)
    netprofit=net_profit()
    netprofit=list(netprofit)
    Decimal(netprofit[4])
    print(netprofit[4])
    netprofit[4]=netprofit[4]-maitenance_sum
    # netprofit=netprofit[4]-maitenance_sum
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



@app.route('/fuel',methods=['POST','GET'])
@driver_protected
def fuel():

    if request.method=='POST':
        litres=request.form['litres']
        truck_id=request.form['truck_id']
        trip_id=request.form['trip_id']
        cpl=request.form['cpl']
        station=request.form['station']
        litres=float(litres)
        cpl=float(cpl)
        l=[trip_id,station,litres,cpl,truck_id]
        insert_fuel_log(l)


    return redirect(url_for('drivers'))



    

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
            selected_truck=None
            selected_driver=None
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
                    flash('Driver,Truck and Trip Assignment In Progress','success')
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
                    odo_start=odo_end
                    cargo_type=shipment_details[5]
                    dispatched_by=get_dispatcher(origin_id)
                    weight=shipment_details[3]
                    destination_id=shipment_details[4]
                    values=[driver_id,truck_id,origin,destination,odo_start,dispatched_by]
                    update_driver_status(selected_driver, 'en_route')
                    update_truck_status(selected_truck, 'en_route')
                    trip_id=insert_trip(values)  
                    flash('Driver and Truck Assigned, Trip Created','success')
                    print(odo_start)
                    print(dispatched_by)
                    print(origin)
                    print(destination)
                    print(driver_id)
                    print(truck_id)
                    acc_id=session.get('acc_id')
                    shipment_values=(acc_id,origin,destination,trip_id,cargo_type,weight,origin_id,destination_id)
                    shipment_id=insert_shipment(shipment_values)
                    print(shipment_id)
                    code = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
                    payment_values=(acc_id,shipment_id,cost,payment_method,code,'completed')
                    insert_payment(payment_values)
            session.pop('cost')
    return redirect(url_for('customers'))




@app.route('/maintenance',methods=['GET','POST'])
@driver_protected
def maintenance():
    truck_data=all_trucks()
    if request.method=='POST':
        truck_id=request.form['target_truck_id']
        odometer=request.form['odometer']
        service_date=request.form['service_date']
        description=request.form['description']
        total=request.form['total']
        issue_date=request.form['issue_date']
        due_date=request.form['due_date']
        invoice_type=request.form['invoice_type']
        
        print(truck_id)
        print(odometer)
        print(service_date)
        print(description)
        print(total)
        print(issue_date)
        print(issue_date)
        print(due_date)
        print(invoice_type)
        invoice_values=[truck_id,description,odometer,service_date,total]
        insert_maintenance_log(invoice_values)
    return render_template('maintenance.html',truck_data=truck_data)

@app.route('/terms')
def terms():
    return render_template('reception.html')


@app.route('/register', methods=['POST','GET'])
def register():
    if request.method=='POST':
        company_name = request.form['company_name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        phone_no=request.form['phone']
        if password != confirm_password:
            flash("Passwords do not match!")
            return redirect(url_for('register'))
        possible_user=check_user(email)
        if possible_user:
            flash('Account Already Registered Please Login','danger')
            return redirect(url_for('login'))
        hashed_password=bcrypt.generate_password_hash(password).decode('utf-8')
        x=[email,hashed_password,'customer']
        a=[company_name,phone_no,'active']
        insert_customer(x,a)
    return render_template('register.html')


@app.route('/dispatchers')
@dispatcher_protected
def dispatchers():
    staff_id=session.get('staff_id')
    staff_email=session.get('staff_email')
    dispatcher_info=get_dispatcher_info(staff_id)
    trips_data=listed_shipments('dispatched',staff_id)
    station_assignment=get_station_assignment(staff_id)
    shipments_handled=get_shipments_handled(staff_id)
    weight_handled=get_weight_handled(staff_id)
    return render_template('dispatchers.html',trips_data=trips_data,
                           dispatcher_info=dispatcher_info,
                           station_assignment=station_assignment,
                           shipments_handled=shipments_handled,
                           weight_handled=weight_handled,
                           staff_email=staff_email
                           )

@app.route('/api/process-route-item', methods=['POST'])
def process_route_item():
    data = request.get_json()
    shipment_id = data.get('shipment_id')
   
    trip_id = set_trip_completed('completed', shipment_id)
    truck_and_driver=get_driver_and_truck_by_trip_id(trip_id)
    update_driver_status(truck_and_driver[0],'completed')
    update_truck_status(truck_and_driver[1],'active')
    print(truck_and_driver)
    return jsonify({'status': 'success', 'message': f'Shipment #{shipment_id} processed.'})

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged Out Successfully', 'success')
    return redirect(url_for('login'))


app.run(debug=True)
server=app.wsgi_app
server.watch('static/')
server.watch('templates/')
