from database2 import expense_against_revenue,get_specific_driver,check_user,get_customer_details,get_customer_shipments,all_destinations,get_dest_coords,get_available_driver,get_truck_start_odo
from flask import session
def month_revenue():
    ear=expense_against_revenue()
    listed_revenue=[]
    for count in ear:
        v=count
        revenue=float(v[1])
    
        listed_revenue.append(revenue)
        if len(listed_revenue)>=12:
            break
    return listed_revenue
def monthly_expense():
    e=expense_against_revenue()
    listed_expense=[]
    for count in e:
        ex=count
        expense=float(ex[2])
        listed_expense.append(expense)
        if len(listed_expense)>=12:
            break
    return listed_expense
operational_months=[i[0] for i in (expense_against_revenue())]
# print(operational_months)
# from database2 import invoice_table
# t=invoice_table()
# r=[i for i in t]
# print(r)
# t='cosi@mail'
# user=check_user(t)
# print(user)
# driver_login=get_specific_driver(user[0])
# print(driver_login)

# driver_login=get_specific_driver(user)
# f=session['driver_id']=driver_login[0]
# print(f)
user_id=4
customer_login=get_customer_details(user_id)
customer_id=101
print(get_customer_shipments(customer_id))
CARGO_RATES = {
    "General Cargo (FMCG & Retail Goods)": 14.00,
    "Dry Bulk & Agricultural Commodities": 13.00,
    "Heavy Industrial & Breakbulk (Metals & Machinery)": 16.00,
    "Cold Chain & Temperature-Controlled (Perishables)": 22.00,
    "Pharmaceutical & Medical Supplies": 20.00,
    "Automotive & Vehicles": 18.00,
    "Liquid Bulk": 19.00,
    "Hazardous Materials (HazMat)": 30.00,
    "High-Value & Secure Cargo": 35.00,
    "Other": 12.00
}
g=get_dest_coords(407)
print(g)
j=get_available_driver('completed')
print(j)
d=get_truck_start_odo(305)
print(d)