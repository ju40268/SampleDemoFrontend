from flask import Flask, redirect, url_for, render_template, request, flash, session, jsonify
import datetime
import mysql.connector as mysql
from functools import wraps
from app.constants import Colors, Manufacturer, VehicleTypes
from app.sql import *
from app import app

MANAGER = "Manager"
INVENTORY_CLERK = "InverntoryClerk"
SALESPERSON = "Salesperson"
SERVICE_WRITER = "ServiceWriter"
ANONYMOUS = "anonymous"
ROLAND_AROUND = "Owner"

db_connection = mysql.connect(host='50.87.253.41', database='charljl4_jj', user='charljl4_team007', password='team007',
                              port=3306)

# https://github.com/ashishsarkar/UserLogin/blob/master/app.py
# check if user logged in
"""
Christie
"""


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please Login with correct credential', 'danger')
            return redirect(url_for('login'))

    return wrap


def roland_login_as_other(session, r):
    cur_role = session['role']
    next_role = session.get('switch_to_role', None)
    return cur_role == ROLAND_AROUND and next_role and next_role == r


def calculate_available_vehicles():
    db_connection.reconnect()
    cursor = db_connection.cursor()
    cursor.execute(AvailableVehicles)
    available_vehicles = cursor.fetchone()
    return available_vehicles[0]


"""
Christie
"""


def load_vehicles():
    d = {}
    db_connection.reconnect()
    print("Connected to:", db_connection.get_server_info())
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM Vehicle;")
    vehicles = cursor.fetchall()
    for i, vehicle in enumerate(vehicles):
        v = {
            'id': vehicle[0],
            'price': vehicle[1],
            'manufacturer': vehicle[2]
        }
        d[i] = v
    return d


"""
Christie
"""


@app.route("/monthly_drilldown/<yyyymm>", methods=["GET"])
def monthly_drilldown_reports(yyyymm):
    # FirstName-LastName-TaxID
    year, month = yyyymm.split("-")[0], yyyymm.split("-")[1]
    db_connection.reconnect()
    cursor = db_connection.cursor()
    cursor.execute(DrilldownReport, (year, month))
    detail_records = cursor.fetchall()
    return render_template('reports/drilldown_reports.html', records=detail_records)


"""
Christie
"""


@app.route("/sales_by_manufacturer", methods=["GET"])
def sales_by_manufacturer_reports():
    db_connection.reconnect()
    cursor = db_connection.cursor()
    cursor.execute(SalesByManufacturer)
    sales_by_manufacturer = cursor.fetchall()
    return render_template('reports/sales_by_manufacturer.html', records=sales_by_manufacturer)


"""
Christie
"""


@app.route("/sales_by_type", methods=["GET"])
def sales_by_type_reports():
    db_connection.reconnect()
    cursor = db_connection.cursor()
    cursor.execute(SalesByType)
    sales_by_type = cursor.fetchall()
    return render_template('reports/sales_by_type.html', records=sales_by_type)


"""
Christie
"""


@app.route("/part_stats", methods=["GET"])
def part_stats_reports():
    db_connection.reconnect()
    cursor = db_connection.cursor()
    cursor.execute(PartStatistics)
    part_stats = cursor.fetchall()
    return render_template('reports/part_stats.html', records=part_stats)


"""
Christie
"""


@app.route("/below_cost", methods=["GET"])
def below_cost_reports():
    db_connection.reconnect()
    cursor = db_connection.cursor()
    cursor.execute(BelowCost)
    below_cost = cursor.fetchall()
    return render_template('reports/below_cost.html', records=below_cost)


"""
Christie
"""


# TODO: add two queries together
@app.route("/gross_income", methods=["GET"])
def gross_income_reports():
    db_connection.reconnect()
    cursor = db_connection.cursor()
    cursor.execute(GrossIncome)
    gross_income = cursor.fetchall()
    return render_template('reports/gross_income.html', records=gross_income)


"""
Christie
"""


@app.route("/monthly_sale", methods=["GET"])
def monthly_sale_reports():
    db_connection.reconnect()
    cursor = db_connection.cursor()
    cursor.execute(MonthlySale)
    monthly_sale = cursor.fetchall()
    return render_template('reports/monthly_sale.html', records=monthly_sale)


"""
Christie
"""


@app.route("/repair_reports", methods=["GET"])
def repair_reports():
    db_connection.reconnect()
    cursor = db_connection.cursor()
    cursor.execute(RepairByType, ('SUV'))
    repair_by_type = cursor.fetchall()
    cursor.execute(RepairByManufacturer, ('Honda'))
    repair_by_manufacturer = cursor.fetchall()
    return render_template('reports/repair_reports.html', records=repair_by_manufacturer)


"""
Christie
"""


@app.route("/avg_inventory", methods=["GET"])
def avg_inventory_reports():
    db_connection.reconnect()
    cursor = db_connection.cursor()
    cursor.execute(AverageInventoryTime)
    avg_inventory = cursor.fetchall()
    return render_template('reports/avg_inventory.html', records=avg_inventory)


"""
Christie
"""


@app.route("/sales_by_color", methods=["GET"])
def sales_by_color_reports():
    db_connection.reconnect()
    cursor = db_connection.cursor()
    cursor.execute(SalesByColor)
    sales_by_color = cursor.fetchall()
    return render_template('reports/sales_by_color.html', records=sales_by_color)


"""
Christie
"""


@app.route("/login", methods=["POST", "GET"])
def login():
    db_connection.reconnect()
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        cur = db_connection.cursor()
        cur.execute("SELECT * FROM RegisteredUser WHERE username=%s AND user_password=%s", (username, password))
        data = cur.fetchone()
        if data:
            session['logged_in'] = True
            session['username'] = data[0]
            session['role'] = data[4]
            flash('Login Successfully', 'success')
            return redirect('home')
        else:
            flash('Invalid Login. Try Again', 'danger')
            return render_template("login.html")
    else:
        return render_template("login.html")


"""
Christie
"""


# logout
@app.route("/logout")
def logout():
    if 'switch_to_role' in session:
        session.pop('switch_to_role')
        return redirect('home')
    else:
        session.clear()
        flash('You are now logged out', 'success')
    return redirect(url_for('login'))


"""
Christie
"""


@app.route('/register', methods=['POST', 'GET'])
def register():
    status = False
    if request.method == 'POST':
        name = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        # cur = mysql.connection.cursor()
        # cur.execute("insert into users(UNAME,UPASS,EMAIL) values(%s,%s,%s)", (name, pwd, email))
        # mysql.connection.commit()
        # cur.close()
        flash('Registration Successfully. Login Here...', 'success')
        return redirect('login')
    return render_template("register.html", status=status)


"""
Christie
"""


@app.route('/add_vehicle', methods=['POST'])
def add_vehicle():
    if request.method == 'POST':
        vin = request.form["vin"]
        invoice_price = request.form["invoice_price"]
        manu_name = request.form["manu_name"]
        inbound_date = request.form["inbound_date"]
        model_year = request.form["model_year"]
        model_name = request.form["model_name"]
        optional_description = request.form["optional_description"]
        vehicleTypeID = request.form["vehicleTypeID"]
        vehicleInputterID = request.form["vehicleInputterID"]
        session['vin'] = vin
        cur = db_connection.cursor()
        cur.execute("insert into Vehicle(VIN, invoice_price, manu_name, inbound_date, model_year, model_name, optional_description, vehicleTypeID, vehicleInputterID)\
        values(%s,%s,%s,%s,%s,%s,%s,%s,%s)", (
        vin, invoice_price, manu_name, inbound_date, model_year, model_name, optional_description, vehicleTypeID,
        vehicleInputterID))
        db_connection.commit()
        cur.close()
        flash('Registration Successfully. Login Here...', 'success')
        return redirect('view_vehicle')
    return render_template("vehicle.html")


"""
Christie
"""


@app.route('/add_customer', methods=['POST', 'GET'])
def add_customer():
    if request.method == 'POST':
        street_address = request.form["street_address"]
        city = request.form["city"]
        state = request.form["state"]
        postal_code = request.form["postal_code"]
        email_address = request.form["email_address"]
        phone_number = request.form["phone_number"]
        is_individual = request.form['is_individual']
        cur = db_connection.cursor()
        cur.execute("INSERT INTO Customer(street_address, city, state, postal_code, email_address, phone_number, is_individual)\
        values(%s,%s,%s,%s,%s,%s,%s)",
                    (street_address, city, state, postal_code, email_address, phone_number, is_individual))
        db_connection.commit()
        cur.close()
        flash('Registration Successfully.', 'success')
        if is_individual == "1":
            return redirect('add_individual')
        else:
            return redirect('add_business')
    return render_template('register_customer.html')


"""
Christie
"""


@app.route('/add_individual', methods=['POST', 'GET'])
def add_individual():
    if request.method == 'POST':
        db_connection.reconnect()
        cur = db_connection.cursor()
        driver_license = request.form["driver_license"]
        ind_first_name = request.form['ind_first_name']
        ind_last_name = request.form['ind_last_name']
        cur.execute("SELECT COUNT(*) FROM Customer")
        customer_count = cur.fetchone()
        cur.execute(InsertIndividual, (driver_license, str(customer_count[0]), ind_first_name, ind_last_name))
        db_connection.commit()
        cur.close()
        flash('Individual {} {} has been added successfully'.format(ind_first_name, ind_last_name), 'success')
    return render_template('register_individual.html')


"""
Christie
"""


@app.route('/add_business', methods=['POST', 'GET'])
def add_business():
    if request.method == 'POST':
        db_connection.reconnect()
        cur = db_connection.cursor()
        tax_id = request.form['tax_id']
        business_name = request.form['business_name']
        title = request.form['title']
        contact_name = request.form['contact_name']
        cur.execute("SELECT COUNT(*) FROM Customer")
        customer_count = cur.fetchone()
        cur.execute(InsertBusiness, (tax_id, str(customer_count[0]), business_name, title, contact_name))
        db_connection.commit()
        cur.close()
        flash('Business {} {} has been added successfully'.format(business_name, title), 'success')
    return render_template('register_business.html')


"""
Christie
"""


@app.route('/view_vehicle', methods=['GET'])
def view_vehicle():
    db_connection.reconnect()
    cursor = db_connection.cursor()
    vin = session['vin']
    cursor.execute("SELECT * FROM Vehicle WHERE VIN=%s", (vin,))
    row_of_car = cursor.fetchone()
    info = {
        'vin': row_of_car[0],
        'invoice_price': row_of_car[1],
        'manu_name': row_of_car[2],
        'inbound_date': row_of_car[3],
        'model_year': row_of_car[4],
        'model_name': row_of_car[5],
        'optional_description': row_of_car[6],
        'vehicle_type': row_of_car[7],
        'vehicle_type_id': row_of_car[8]
    }
    return render_template("vehicle_details.html", params=info)


"""
Christie
"""


@app.route("/search_data", methods=["POST", "GET"])
def public_search():
    if request.method == 'POST':
        print(request.form)
        # vin = request.form['vin']
        # vehicle_type = request.form['vehicle_type']
        # manufacturer = request.form['manufacturer']
        # model_year = request.form['model_year']
        # color = request.form['color']
        # list_price = request.form['list_price']
        # key_word = request.form['key_word']
        # db_connection.reconnect()
        # cursor = db_connection.cursor()
        # cursor.execute("SELECT * FROM Vehicle WHERE VIN=%s", (vin,))
        # matches = cursor.fetchall()
        # records = []
        # for m in matches:
        #     info = {
        #         'vin': m[0],
        #         'invoice_price': m[1],
        #         'manu_name': m[2],
        #         'inbound_date': m[3],
        #         'model_year': m[4],
        #         'model_name': m[5],
        #         'optional_description': m[6],
        #         'vehicle_type': m[7],
        #         'vehicle_type_id': m[8]
        #     }
        #     records.append(info)
    records = []
    if session['role'] == SALESPERSON:
        return render_template("salesperson_filter_results.html", records=records)
    return render_template("manager_filter_results.html", records=records)


"""
Christie
"""


@app.route("/search_customer", methods=["POST", "GET"])
def search_customer():
    db_connection.reconnect()
    if request.method == 'POST':
        driver_license = request.form['driver_license']
        tax_id = request.form['tax_id']
        cursor = db_connection.cursor()
        cursor.execute(FilterCustomer, (driver_license,))
        customers = cursor.fetchall()
        print("[Search Customer]: driver license: {}, tax_id: {}".format(driver_license, tax_id))
        records = []
        for customer in customers:
            info = {
                'customer_id': customer[0],
                'street_address': customer[1],
                'city': customer[2],
                'state': customer[3],
                'postal_code': customer[4],
                'email': customer[5],
                'phone': customer[6],
                'is_individual': customer[7]
            }
            records.append(info)

    if session['role'] == SALESPERSON:
        return render_template("salesperson_customer_filter_results.html", records=records,
                               vin=session['propose_to_sale'])
    return render_template("customer_filter_results.html", records=records)


@app.route("/sale_vehicle/<select_vin>", methods=["POST"])
def sale_vehicle(select_vin):
    session['propose_to_sale'] = select_vin
    return render_template("salesperson_customer_search.html")


@app.route('/add_order/<vin>/<customer_id>', methods=['GET'])
def add_order(vin, customer_id):
    current_date = datetime.datetime.now()
    return render_template("order.html", vin=vin, customer_id=customer_id, role='dyu', current_date=current_date)


# sold_price > 95% * invoice_price
@app.route('/submit_order', methods=['POST'])
def submit_order():
    current_date = datetime.datetime.now()
    if request.method == 'POST':
        vin = request.form['vin']
        sales_inputter_id = request.form['sales_inputter_id']
        sold_price = request.form['sold_price']
        customer_id = request.form['customer_id']
        db_connection.reconnect()
        cur = db_connection.cursor()
        cur.execute(InsertPurchase, (sales_inputter_id, vin, customer_id, current_date, sold_price))
        db_connection.commit()
        cur.close()
        flash('Order Submitted Correctly!', 'info')
    return redirect('home')


@app.route("/switch_role", methods=["POST"])
def switch_role():
    session['switch_to_role'] = request.form['switch']
    print(session)
    return redirect(request.referrer)


"""
Christie
"""


def dynamic_dropdown():
    db_connection.reconnect()
    cursor = db_connection.cursor()
    cursor.execute(SelectDistinctVIN)
    vin = cursor.fetchall()
    cursor.execute(SelectDistinctTypeName)
    vehicles_types = cursor.fetchall()
    cursor.execute(SelectDistinctModelYear)
    model_years = cursor.fetchall()
    cursor.execute(SelectDistinctColor)
    colors = cursor.fetchall()
    cursor.execute(SelectDistinctManufacturer)
    manufacturers = cursor.fetchall()
    list_vin = map(lambda x: x[0], vin)
    list_vehicles_types = map(lambda x: x[0], vehicles_types)
    list_model_year = map(lambda x: x[0], model_years)
    list_of_colors = map(lambda x: x[0], colors)
    list_of_manufacturers = map(lambda x: x[0], manufacturers)
    d = {
        'vin' : list_vin,
        'vehicles_types' : list_vehicles_types,
        'model_year': list_model_year,
        'colors': list_of_colors,
        'manufacturers': list_of_manufacturers
    }
    return d


@app.route('/home', methods=['GET'])
@is_logged_in
def index():
    role = session['role']
    dropdown_data = dynamic_dropdown()
    if role == MANAGER or roland_login_as_other(session, MANAGER):
        available_car_amount = calculate_available_vehicles()
        return render_template("manager.html",
                               vin=dropdown_data.get('vin', []),
                               colors=dropdown_data.get('colors', []),
                               manufacturers=dropdown_data.get('manufacturers', []),
                               vehicles_types=dropdown_data.get('vehicles_types', []),
                               model_year=dropdown_data.get('model_year', []),
                               available_car_amount=available_car_amount)
    elif role == INVENTORY_CLERK or roland_login_as_other(session, INVENTORY_CLERK):
        return render_template("clerk.html", params=role)
    elif role == SERVICE_WRITER or roland_login_as_other(session, SERVICE_WRITER):
        return render_template("writer.html", params=role)
    elif role == SALESPERSON or roland_login_as_other(session, SALESPERSON):
        return render_template("salesperson.html", params=role, colors=Colors, manufacturers=Manufacturer,
                               vehicles_types=VehicleTypes)
    elif role == ROLAND_AROUND:
        return render_template('roland.html', colors=Colors, manufacturers=Manufacturer, vehicles_types=VehicleTypes)
