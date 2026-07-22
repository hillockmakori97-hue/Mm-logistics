import psycopg2
conn=psycopg2.connect(
    host='localhost',
    port=5432,
    user='postgres',
    dbname='mm_logistics',
    password='rs3040bt'
)
curr=conn.cursor()

def get_driver_profile(driver_id):
    # Parameterized query executing directly with the single-item tuple
    curr.execute('''
        SELECT 
            d.driver_id,
            d.driver_name,
            d.phone_number,
            d.license_number,
            d.license_type,
            d.license_expiry,
            CASE 
                WHEN d.license_expiry < CURRENT_DATE THEN 'EXPIRED'
                WHEN d.license_expiry <= CURRENT_DATE + INTERVAL '30 days' THEN 'EXPIRING SOON'
                ELSE 'VALID'
            END AS license_status,
            d.status AS current_status,
            (SELECT trk.plate 
             FROM trips t 
             JOIN trucks trk ON t.truck_id = trk.truck_id 
             WHERE t.driver_id = d.driver_id 
             ORDER BY t.dispatch_time DESC 
             LIMIT 1) AS last_driven_truck
        FROM drivers d
        WHERE d.driver_id = %s
    ''', (driver_id,))
    return curr.fetchone()

def get_available_driver(status):
    curr.execute('select driver_id from drivers where status=%s',(status,))
    return curr.fetchall()


def get_driver_kpis(driver_id):
    # Pulls aggregations for the matching driver profile index
    curr.execute('''
        SELECT 
            COUNT(DISTINCT t.trip_id) AS total_trips,
            COUNT(DISTINCT t.trip_id) FILTER (WHERE t.status = 'Completed') AS completed_trips,
            COALESCE(SUM(CASE WHEN i.invoice_type = 'Toll' THEN i.total_amount END), 0.00) AS total_tolls,
            COALESCE(SUM(CASE WHEN i.invoice_type = 'Fine' THEN i.total_amount END), 0.00) AS total_fines
        FROM trips t
        LEFT JOIN invoices i ON t.trip_id = i.trip_id
        WHERE t.driver_id = %s
    ''', (driver_id,))
    return curr.fetchone()


def get_driver_trip_history(driver_id):
    # Returns all matched operational runs for the historical table data
    curr.execute('''
        SELECT 
            t.trip_id,
            t.origin || ' to ' || t.destination AS route,
            trk.plate AS truck_plate,
            t.dispatch_time,
            t.status AS trip_status,
            (COALESCE(t.odo_end, t.odo_start) - t.odo_start) AS distance_km,
            COALESCE(SUM(CASE WHEN i.invoice_type = 'Toll' THEN i.total_amount END), 0.00) AS trip_tolls,
            COALESCE(SUM(CASE WHEN i.invoice_type = 'Fine' THEN i.total_amount END), 0.00) AS trip_fines
        FROM trips t
        JOIN trucks trk ON t.truck_id = trk.truck_id
        LEFT JOIN invoices i ON t.trip_id = i.trip_id
        WHERE t.driver_id = %s
        GROUP BY t.trip_id, t.origin, t.destination, trk.plate, t.dispatch_time, t.status, t.odo_end, t.odo_start
        ORDER BY t.dispatch_time DESC
    ''', (driver_id,))
    return curr.fetchall()
def total_revenue():
    curr.execute('''
        SELECT 
            SUM(subtotal_amount) AS total_revenue_before_tax,
            SUM(tax_amount) AS total_tax_collected,
            SUM(total_amount) AS gross_revenue_with_tax
        FROM 
            invoices
        WHERE 
            invoice_type = 'Standard';
                
            ''')
    result=curr.fetchone()
    return result
def total_dispatches():
    curr.execute('''
        SELECT 
            COUNT(*) AS total_dispatches,
            COUNT(*) FILTER (WHERE status = 'en_route') AS active_dispatches
        FROM 
            trips;
                 ''')
    return curr.fetchone()



def active_trips():
    curr.execute('''
        SELECT COUNT(*) AS active_trips_count
        FROM trips
        WHERE status = 'en_route';
        ''')
    return curr.fetchone()
def net_profit():
    curr.execute(''' WITH revenue AS (
    -- 1. Incoming cash flow from paid invoices
    SELECT COALESCE(SUM(total_amount), 0) AS total_revenue 
    FROM invoices 
    WHERE status = 'paid'
),
fuel AS (
    -- 2. Real vehicle fuel costs (litres * cost per litre)
    SELECT COALESCE(SUM(litres_fueled * cost_per_litre), 0) AS total_fuel_cost 
    FROM fuel_logs
),
driver_payouts AS (
    -- 3. Total fixed base salaries + dynamic per-trip driver payout rates
    SELECT 
        (SELECT COALESCE(SUM(base_salary), 0) FROM drivers WHERE status != 'suspended') AS total_base,
        COALESCE(SUM(d.per_trip_rate), 0) AS total_trip_bonuses
    FROM trips t
    JOIN drivers d ON t.driver_id = d.driver_id
    WHERE t.status = 'completed'
),
office_payouts AS (
    -- 4. Corporate salary overhead
    SELECT COALESCE(SUM(monthly_salary), 0) AS total_office
    FROM office_staff
    WHERE is_active = TRUE
)
SELECT 
    r.total_revenue AS gross_revenue,
    f.total_fuel_cost AS fuel_expenses,
    (dp.total_base + dp.total_trip_bonuses) AS driver_payroll,
    op.total_office AS office_payroll,
    -- Core Calculation: Revenue - Fuel - Driver Payroll - Office Payroll
    (
        r.total_revenue 
        - f.total_fuel_cost 
        - (dp.total_base + dp.total_trip_bonuses) 
        - op.total_office
    ) AS true_net_profit
FROM revenue r, fuel f, driver_payouts dp, office_payouts op;
    ''')
    return curr.fetchone()
def completed_trips():
    curr.execute('''
SELECT COUNT(*) AS total_completed_trips
FROM trips
WHERE status = 'completed';
            ''')
    return curr.fetchone()
def expense_against_revenue():
    curr.execute('''
                 WITH monthly_revenue AS (
    -- Total standard billing collections from customers
    SELECT 
        DATE_TRUNC('month', issue_date) AS month,
        SUM(total_amount) AS total_revenue
    FROM invoices
    WHERE invoice_type = 'Standard' AND EXTRACT(YEAR FROM issue_date) = 2026
    GROUP BY 1
),
all_cash_outflows AS (
    -- 1. Direct pump purchases (litres * cost)
    SELECT 
        DATE_TRUNC('month', logged_at) AS month,
        (litres_fueled * cost_per_litre) AS outflow_amount
    FROM fuel_logs
    WHERE EXTRACT(YEAR FROM logged_at) = 2026
    
    UNION ALL
    
    -- 2. Operational expense invoices + Maintenance costs linked via invoice_id
    -- Matches Tolls, Fines, Fuel, and Maintenance invoices
    SELECT 
        DATE_TRUNC('month', i.issue_date) AS month,
        i.total_amount AS outflow_amount
    FROM invoices i
    LEFT JOIN maintenance_logs m ON CAST(i.invoice_id AS VARCHAR) = m.invoice_id
    WHERE (i.invoice_type IN ('Fuel', 'Toll', 'Fine') OR m.invoice_id IS NOT NULL)
      AND EXTRACT(YEAR FROM i.issue_date) = 2026

    UNION ALL
    
    -- 3. Driver Payroll (Aggregating base_salary across active/listed drivers)
    SELECT 
        months.month,
        SUM(d.base_salary) AS outflow_amount
    FROM drivers d
    CROSS JOIN (
        SELECT GENERATE_SERIES(
            '2026-01-01'::date, 
            '2026-12-01'::date, 
            '1 month'::interval
        )::date AS month
    ) months
    GROUP BY months.month
),
aggregated_expenses AS (
    SELECT 
        month,
        SUM(outflow_amount) AS total_expenses
    FROM all_cash_outflows
    GROUP BY 1
)
SELECT 
    TO_CHAR(COALESCE(r.month, e.month), 'YYYY-MM') AS operational_month,
    COALESCE(r.total_revenue, 0.00) AS total_revenue,
    COALESCE(e.total_expenses, 0.00) AS total_expenses,
    (COALESCE(r.total_revenue, 0.00) - COALESCE(e.total_expenses, 0.00)) AS net_profit
FROM monthly_revenue r
FULL OUTER JOIN aggregated_expenses e ON r.month = e.month
ORDER BY COALESCE(r.month, e.month) ASC;
    ''')
    return curr.fetchall()
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

# print(expense_against_revenue())
def invoice_table():
    curr.execute(' select invoice_id,invoice_type,status,total_amount from invoices')
    return curr.fetchall()
def payments_table():
    curr.execute('select payment_id,shipment_id,amount,payment_status from payments')
    return curr.fetchall()
def check_user(email):
    curr.execute('select * from users where email=%s',(email,))
    return curr.fetchone()

def get_specific_driver(user_id):
    curr.execute('select driver_id from drivers where user_id=%s',(user_id,))
    return curr.fetchone()
def shipments_per_customer(user_id):
    curr.execute('select * from shipments where customer_id=%s',(user_id,))
    return curr.fetchall()
def get_customer_details(user_id):
    curr.execute('''
    SELECT 
        customers.customer_id,
        users.user_id,
        users.email,
        customers.company_name,
        customers.account_status
    FROM customers 
    INNER JOIN users ON users.user_id = customers.user_id 
    WHERE users.user_id =%s''',(user_id,))
    return curr.fetchone()


def get_customer_shipments(customer_id):
    curr.execute('''SELECT
    COUNT(s.shipment_id) AS total_orders 
FROM customers c
LEFT JOIN shipments s ON c.customer_id = s.customer_id where c.customer_id=%s
GROUP BY c.customer_id;
            ''',(customer_id,))
    return curr.fetchone()
def sidebar_logs(customer_id):
    curr.execute('''
        SELECT 
            t.origin, 
            t.destination, 
            TO_CHAR(t.dispatch_time, 'DD Mon') AS formatted_date,
            t.status,
            t.trip_id
        FROM trips t
        JOIN shipments s ON t.trip_id = s.trip_id
        WHERE s.customer_id = %s
        ORDER BY t.dispatch_time DESC;
    ''', (customer_id,))
    return curr.fetchall()

def all_destinations():
    curr.execute('select * from destinations')
    return curr.fetchall()
def insert_shipment(values):
    curr.execute('''
        INSERT INTO shipments (
            customer_id, origin, destination, trip_id, 
            cargo_description, weight_kg, origin_id, destination_id
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) 
        RETURNING shipment_id;
    ''', values)
    conn.commit()
    result = curr.fetchone()
    return result[0] if result else None



CARGO_RATES = {
    "General Cargo (FMCG & Retail Goods)": 120.00,
    "Heavy Industrial & Breakbulk (Metals & Machinery)": 160.00,
    "Dry Bulk & Agricultural Commodities": 130.00,
    "Cold Chain & Temperature-Controlled (Perishables)": 220.00,
    "Pharmaceutical & Medical Supplies": 200.00,
    "Hazardous Materials (HazMat)": 300.00,
    "Liquid Bulk": 250.00,
    "Automotive & Vehicles": 180.00,
    "High-Value & Secure Cargo": 350.00,
    "Other": 100.00
}
def get_dest_coords(destination_id):
    curr.execute(
        'select latitude, longitude from destinations where destination_id=%s',(destination_id,)
    )
    return curr.fetchone()
def get_categories():
    curr.execute('select * from categories')
    return curr.fetchall()
def get_driver():
    curr.execute("select driver_id from drivers where status='completed'")
    return curr.fetchall()
def get_dest_name(dest_id):
    curr.execute('select city from destinations where destination_id=%s',(dest_id,))
    return curr.fetchone()
def get_truck(status):
    curr.execute('select truck_id from trucks where status=%s',(status,))
    return curr.fetchall()

def get_truck_end_odo(truck_id):
    curr.execute('select odo_end from trips where truck_id=%s',(truck_id,))
    return curr.fetchone()
def get_dispatcher(destination_id):
    curr.execute('select managed_by_staff_id from destinations where destination_id=%s',(destination_id,))
    return curr.fetchone()
def insert_trip(values):
    curr.execute('''
        INSERT INTO trips (
            driver_id, truck_id, origin, destination, odo_start, dispatched_by
        ) VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING trip_id; 
    ''', values)
    conn.commit()
    result = curr.fetchone()
    return result[0] 

