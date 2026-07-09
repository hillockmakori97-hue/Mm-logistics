from database2 import expense_against_revenue,get_specific_driver,check_user
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