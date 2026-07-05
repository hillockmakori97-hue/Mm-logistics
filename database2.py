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

print(net_profit())