import psycopg2
conn=psycopg2.connect(
    host='localhost',
    port=5432,
    user='postgres',
    dbname='mm_logistics',
    password='rs3040bt'
)
                            # Getting all data from all my tables

# invoices 
curr=conn.cursor()
def all_invoices():
    curr.execute('select * from invoices')
    invoices=curr.fetchall()
    return invoices
# print(all_invoices())



# users 
def all_users():
    curr.execute('select * from users')
    users=curr.fetchall()
    return users
# print(all_users())



# All trucks function
def all_trucks():
    curr.execute('select * from trucks')
    trucks=curr.fetchall()
    return trucks
 
# print(all_trucks())




# All customers function
def all_customers():
    curr.execute('select * from customers')
    customers=curr.fetchall()
    return(customers)

# print(all_customers())


# All destinations function 
def all_destinations():
    curr.execute('select * from destinations')
    destinations=curr.fetchall()
    return destinations

# print(all_destinations())



# All shipments function 
def all_shipments():
    curr.execute('select * from shipments')
    shipments=curr.fetchall()
    return shipments

# print(all_shipments())



#All payments function 
def all_payments():
    curr.execute('select * from payments')
    payments=curr.fetchall()
    return payments

# print(all_payments())



# All cargo types function 
def all_cargo_types():
    curr.execute('select * from cargo_types')
    cargo_types=curr.fetchall()
    return cargo_types

# print(all_cargo_types())



# All maintenance logs
def all_maintenance_logs():
    curr.execute('select * from maintenance_logs')
    maintenance_logs=curr.fetchall()
    return maintenance_logs

# print(all_maintenance_logs())

# All fuel logs 
def all_fuel_logs():
    curr.execute('select * from fuel_logs')
    fuel_logs=curr.fetchall()
    return fuel_logs

# print(all_fuel_logs())

#                       inseting data into my tables 
# inserting into cargotypes 
def insert_cargo_types(values):
    curr.execute('insert into cargo_types (type_name,base_multiplier,handling_notes) values(%s,%s,%s)',values)
    conn.commit()
# insert_cargo_types(('elecronics',1.5,'store in a cool dry place'))

# inserting into customers( user level )
# nb ,,,,revisit this when building your flask ,,,,,,,,,remember user access ,,,,,placing an ooder or just addig user shold only be called when logged out 
# # Micro function

    

def insert_customer(user_values,customer_values):
    curr.execute('insert into users (email,password,role) values(%s,%s,%s) returning user_id',user_values)
    user_id=curr.fetchone()[0]
    all_values=customer_values+(user_id,)
    curr.execute('INSERT INTO customers (company_name, contact_phone, account_status, user_id) VALUES (%s, %s, %s, %s)',all_values)
    conn.commit()



# insert destination
def insert_destination(values):
    curr.execute('insert into destinations (location_name,city,street_address,contact_person,contact_phone) values (%s,%s,%s,%s,%s)',values)
    conn.commit()



# inserting driver
def insert_driver(values):
    curr.execute('insert into drivers (driver_name,phone_number,license_number,license_type,license_expiry,status) values (%s,%s,%s,%s,%s,%s)',values)
    conn.commit()



# insering fuel logs
def insert_fuel_log(values):
    curr.execute('insert into fuel_logs (trip_id, station_name, litres_fueled, cost_per_litre) values (%s, %s, %s, %s)', values)
    conn.commit()




# inserting invoices
def insert_invoice(values):
    curr.execute('insert into invoices (shipment_id, subtotal_amount, tax_amount, total_amount, status, issue_date, due_date, invoice_type, trip_id) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)', values)
    conn.commit()




#  inserting maintenance log
def insert_maintenance_log(Invoice_values,maintenance_values):
    curr.execute('insert into invoices (shipment_id, subtotal_amount, tax_amount, total_amount, status, issue_date, due_date, invoice_type, trip_id) values (%s, %s, %s, %s, %s, %s, %s, %s, %s) returning invoice_id', Invoice_values)
    all_values=maintenance_values+(curr.fetchone()[0],)
    curr.execute('insert into maintenance_logs (truck_id, service_description, odometer_at_service, service_date, invoice_id) values (%s, %s, %s, %s, %s)',all_values)
    conn.commit()



# inserting_payment
def insert_payment(values):
    curr.execute('insert into payments (customer_id, shipment_id, amount, payment_method, transaction_reference, payment_date, payment_status) values (%s, %s, %s, %s, %s, %s, %s)', values)
    conn.commit()



# inserting trip
def insert_trip(values):
    curr.execute('''
        INSERT INTO trips (
            truck_id, driver_id, origin, destination, 
            odo_start, odo_end, actual_arrival_time, status, dispatched_by
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', values)
    conn.commit()



# inserting_shipments
def insert_shipment(values):
    curr.execute('''
        INSERT INTO shipments (
            customer_id, origin, destination, trip_id, 
            cargo_description, weight_kg, status, origin_id, destination_id
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', values)
    conn.commit()




# inserting trucks
def insert_truck(values):
    curr.execute('''
        INSERT INTO trucks (
            plate, model, axle_configuration, status, expected_kpl, 
            fuel_capacity_liters, last_insurance_date, next_insurance_due, 
            last_maintenance_date, next_maintenance_due
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', values)
    conn.commit()




# inserting users
def insert_user(values):
    curr.execute('''
        INSERT INTO users (email, password, role) 
        VALUES (%s, %s, %s)
    ''', values)
    conn.commit()





                                        # Analysis and joins



# driver expenses
def driver_expenses():
    curr.execute('''
                    SELECT 
                        d.driver_id,
                        d.driver_name,
                        COUNT(DISTINCT tr.trip_id) AS total_trips_tracked,
                        COALESCE(SUM(CASE WHEN i.invoice_type = 'Toll' THEN i.total_amount END), 0.00) AS total_toll_expenses,
                        COALESCE(SUM(CASE WHEN i.invoice_type = 'Fine' THEN i.total_amount END), 0.00) AS total_fine_accumulated
                    FROM drivers d
                    LEFT JOIN trips tr ON d.driver_id = tr.driver_id
                    LEFT JOIN invoices i ON tr.trip_id = i.trip_id
                    GROUP BY d.driver_id, d.driver_name
                    ORDER BY total_fine_accumulated DESC
                ''')
    return curr.fetchall()
    


# Finding toll and fine expenses against commercial revenue


def fine_and_toll_expences():
    curr.execute('''
                    SELECT 
                        COUNT(invoice_id) AS total_invoices_issued,
                        COALESCE(SUM(CASE WHEN invoice_type = 'Standard' THEN total_amount END), 0.00) AS gross_commercial_revenue,
                        COALESCE(SUM(CASE WHEN invoice_type = 'Toll' THEN total_amount END), 0.00) AS absolute_toll_fees,
                        COALESCE(SUM(CASE WHEN invoice_type = 'Fine' THEN total_amount END), 0.00) AS absolute_fine_losses
                    FROM invoices
                 ''')
    return curr.fetchall()
# print(fine_and_toll_expences())




# Driver profit and fine/toll analysis


def driver_profit_analysis():
    curr.execute('''
                        SELECT 
                            tr.trip_id,
                            d.driver_name,
                            t.plate AS truck_plate,
                            -- Revenue from shipments on this trip
                            COALESCE(SUM(CASE WHEN i.invoice_type = 'Standard' THEN i.total_amount END), 0.00) AS trip_revenue,
                            -- Deductions
                            COALESCE(SUM(CASE WHEN i.invoice_type = 'Toll' THEN i.total_amount END), 0.00) AS trip_tolls,
                            COALESCE(SUM(CASE WHEN i.invoice_type = 'Fine' THEN i.total_amount END), 0.00) AS trip_fines,
                            -- Net Calculation
                            (COALESCE(SUM(CASE WHEN i.invoice_type = 'Standard' THEN i.total_amount END), 0.00) - 
                            COALESCE(SUM(CASE WHEN i.invoice_type = 'Toll' THEN i.total_amount END), 0.00) - 
                            COALESCE(SUM(CASE WHEN i.invoice_type = 'Fine' THEN i.total_amount END), 0.00)) AS net_trip_profit
                        FROM trips tr
                        JOIN drivers d ON tr.driver_id = d.driver_id
                        JOIN trucks t ON tr.truck_id = t.truck_id
                        LEFT JOIN shipments s ON tr.trip_id = s.trip_id
                        LEFT JOIN invoices i ON (s.shipment_id = i.shipment_id OR tr.trip_id = i.trip_id)
                        GROUP BY tr.trip_id, d.driver_name, t.plate
                        ORDER BY net_trip_profit DESC
                ''')
    return curr.fetchall()



# fuel and salary payments
def fuel_and_salary_payments():
    curr.execute('''
                    SELECT 
                        i.invoice_id,
                        i.invoice_type,
                        i.total_amount,
                        i.status AS payment_status,
                        i.issue_date,
                        i.due_date,
                        c.company_name AS client_name,
                        d.driver_name,
                        t.plate AS truck_plate,
                        tr.trip_id
                    FROM invoices i
                    LEFT JOIN shipments s ON i.shipment_id = s.shipment_id
                    LEFT JOIN customers c ON s.customer_id = c.customer_id
                    LEFT JOIN trips tr ON (i.trip_id = tr.trip_id OR s.trip_id = tr.trip_id)
                    LEFT JOIN drivers d ON tr.driver_id = d.driver_id
                    LEFT JOIN trucks t ON tr.truck_id = t.truck_id
                    ORDER BY i.status ASC, i.due_date ASC
                ''')
    return curr.fetchall()





# Driver salary raise eligibility
def d_raise_eligibility():
    curr.execute('''
                    SELECT 
                        d.driver_id,
                        d.driver_name,
                        COUNT(DISTINCT tr.trip_id) AS total_completed_trips,
                        COUNT(CASE WHEN i.invoice_type = 'Fine' THEN 1 END) AS traffic_fines_count,
                        COALESCE(SUM(CASE WHEN i.invoice_type = 'Fine' THEN i.total_amount END), 0.00) AS total_fine_cost,
                        CASE 
                            WHEN COUNT(DISTINCT tr.trip_id) = 0 THEN 'No Trips Conducted Yet'
                            WHEN COUNT(CASE WHEN i.invoice_type = 'Fine' THEN 1 END) = 0 THEN 'ELIGIBLE FOR MAXIMUM RAISE (Clean Record)'
                            WHEN COUNT(CASE WHEN i.invoice_type = 'Fine' THEN 1 END) <= 2 THEN 'ELIGIBLE FOR MODERATE RAISE (Low Infractions)'
                            ELSE 'INELIGIBLE FOR RAISE (High Infraction Frequency)'
                        END AS raise_evaluation_status
                    FROM drivers d
                    LEFT JOIN trips tr ON d.driver_id = tr.driver_id
                    LEFT JOIN invoices i ON tr.trip_id = i.trip_id
                    GROUP BY d.driver_id, d.driver_name
                    ORDER BY traffic_fines_count ASC, total_completed_trips DESC
                ''')
    return curr.fetchall()
# print(d_raise_eligibility())





# profit per month 
def profit_per_month():
    curr.execute('''SELECT 
                    TO_CHAR(i.issue_date, 'YYYY-MM') AS financial_month,
                    COALESCE(SUM(CASE WHEN i.invoice_type = 'Standard' THEN i.total_amount END), 0.00) AS gross_revenue,
                    COALESCE(SUM(CASE WHEN i.invoice_type = 'Toll' THEN i.total_amount END), 0.00) AS total_toll_expenses,
                    COALESCE(SUM(CASE WHEN i.invoice_type = 'Fine' THEN i.total_amount END), 0.00) AS total_fine_expenses,
                    (
                        COALESCE(SUM(CASE WHEN i.invoice_type = 'Standard' THEN i.total_amount END), 0.00) - 
                        COALESCE(SUM(CASE WHEN i.invoice_type = 'Toll' THEN i.total_amount END), 0.00) - 
                        COALESCE(SUM(CASE WHEN i.invoice_type = 'Fine' THEN i.total_amount END), 0.00)
                    ) AS net_profit
                FROM invoices i
                GROUP BY TO_CHAR(i.issue_date, 'YYYY-MM')
                ORDER BY financial_month DESC
                ''')
    return curr.fetchall()





# monthly revenue
def month_revenue_and_expense(month_number):
    curr.execute('''
                    SELECT 
                        COALESCE(SUM(CASE WHEN invoice_type = 'Standard' THEN total_amount END), 0.00) AS gross_revenue,
                        COALESCE(SUM(CASE WHEN invoice_type = 'Toll' THEN total_amount END), 0.00) AS toll_expenses,
                        COALESCE(SUM(CASE WHEN invoice_type = 'Fine' THEN total_amount END), 0.00) AS fine_expenses,
                        
                        -- Total Expenses Calculation
                        (COALESCE(SUM(CASE WHEN invoice_type = 'Toll' THEN total_amount END), 0.00) + 
                        COALESCE(SUM(CASE WHEN invoice_type = 'Fine' THEN total_amount END), 0.00)) AS total_expenses,
                        
                        -- Net Profit Calculation
                        (COALESCE(SUM(CASE WHEN invoice_type = 'Standard' THEN total_amount END), 0.00) - 
                        COALESCE(SUM(CASE WHEN invoice_type = 'Toll' THEN total_amount END), 0.00) - 
                        COALESCE(SUM(CASE WHEN invoice_type = 'Fine' THEN total_amount END), 0.00)) AS net_profit
                    FROM invoices
                    WHERE EXTRACT(MONTH FROM issue_date) =%s 
                ''',(month_number,)
                )
    return curr.fetchone()




# toll fees per month
def toll_fees_per_month():
    curr.execute('''
                    SELECT 
                        TO_CHAR(issue_date, 'YYYY-MM') AS financial_month,
                        COUNT(invoice_id) AS total_toll_gates_passed,
                        SUM(total_amount) AS total_toll_fees_paid
                    FROM invoices
                    WHERE invoice_type = 'Toll'
                    GROUP BY TO_CHAR(issue_date, 'YYYY-MM')
                    ORDER BY financial_month DESC
                ''')
    return curr.fetchall()
# print(toll_fees_per_month())



# toll fees per year
def toll_fees_per_year():
    curr.execute('''
                    SELECT 
                        TO_CHAR(issue_date, 'YYYY') AS financial_year,
                        COUNT(invoice_id) AS total_toll_gates_passed,
                        SUM(total_amount) AS total_toll_fees_paid
                    FROM invoices
                    WHERE invoice_type = 'Toll'
                    GROUP BY TO_CHAR(issue_date, 'YYYY')
                    ORDER BY financial_year DESC
                ''')
    return curr.fetchall()
print(toll_fees_per_year())
