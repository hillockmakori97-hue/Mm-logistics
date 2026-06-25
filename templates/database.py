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

#                       joins and getting specific records from my tables