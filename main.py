import random
from flask import Flask, flash, render_template, request, session, redirect, url_for
import datetime
from passlib.context import CryptContext
import db as db

app = Flask(__name__)
app.secret_key = 'asta'  # Use a secure secret key in production

# Password hashing context
password_ctx = CryptContext(schemes=['bcrypt'])

# Helper function to check if a user exists
def user_exists(conn, table, email_column, email):
    with conn.cursor() as cur:
        cur.execute(f"SELECT * FROM {table} WHERE {email_column} = %s;", (email,))
        return cur.fetchone()
def is_valid_phone_number(phone):
    """Validate phone numbers to contain only numbers and have a length between 10 and 16."""
    return phone.isdigit() and 10 <= len(phone) <= 16

def find_magasin_by_gerant(db_conn, id_ger):
    """
    Find magasin(s) by manager ID.

    :param db_conn: A psycopg2 connection object to the PostgreSQL database.
    :param id_ger: The manager ID (idGerant) to search for.
    """

    with db_conn.cursor() as cur:
        # Query to find magasin by manager ID
        query = """
            SELECT idMag
            FROM magasin
            WHERE idGer = %s
        """
        cur.execute(query, (int(id_ger),))
        result = cur.fetchone()
    return result


# Routes
# Error page
@app.route("/error")
def show_error_page():
    return render_template("error.html")

@app.route("/gerant_login")
def gerant_login():
    if 'user' not in session:
        return render_template("gerant_login.html")
    else:
        flash("You already logged in.", "warning")
        return redirect("show_error_message")
@app.route("/employe_login")
def employe_login():
    if 'user' not in session:
        return render_template("employe_login.html")
    else:
        flash("You already logged in.", "warning")
        return redirect("show_error_message")

@app.route("/client_login")
def client_login():
    if 'user' not in session:
        return render_template("client_login.html")
    else:
        flash("You already logged in.", "warning")
        return redirect("show_error_message")

@app.route("/gerant_register")
def gerant_register():
    return render_template("gerant_register.html")
@app.route("/employe_register")
def employe_register():
    return render_template("employe_register.html")
@app.route("/client_register")
def client_register():
    return render_template("client_register.html")



# Create new account
@app.route("/create_new_account", methods=["POST"])
def create_account():
    if request.method == 'POST':
        firstname = request.form['Firstname'].lower().capitalize()
        name = request.form['Name'].lower().capitalize()
        mail = request.form['Email'].lower()
        tel = request.form['Phone']
        mdp = request.form['Password']
        country = request.form["Country"]
        role = request.form["Role"]

        if not all([firstname, name, mail, tel, mdp, country, role]):
            flash("All fields are required.", "danger")
            return redirect(url_for("show_error_page"))

        if len(tel) < 9:
            flash("Phone number must be at least 9 digits.", "warning")
            return redirect(url_for("show_error_page"))
#modify this later
        hashed_password = password_ctx.hash(mdp)
        print(hashed_password)
        tel = country + tel

        with db.connect() as conn:
            if role == "Manager":
                if not user_exists(conn, "gerant", "mailGer", mail):
                    with conn.cursor() as cur:
                        cur.execute(
                            """
                            INSERT INTO gerant(nomGer, prenomGer, mailGer, telGer, mdpGer)
                            VALUES (%s, %s, %s, %s, %s);
                            """,
                            (name, firstname, mail, tel, hashed_password),
                        )
                    flash("Manager account created successfully.", "success")
                    return redirect(url_for("gerant_login"))
                else:
                    flash("An account with this email already exists.", "warning")
            elif role == "Employe":
                if not user_exists(conn, "employe", "mailEmp", mail):
                    with conn.cursor() as cur:
                        cur.execute(
                            """
                            INSERT INTO employe(nomEmp, prenomEmp, mailEmp, telEmp, mdpEmp)
                            VALUES (%s, %s, %s, %s, %s);
                            """,
                            (name, firstname, mail, tel, hashed_password ),
                        )
                    flash("Employee account created successfully.", "success")
                    return redirect(url_for("employe_login"))
                else:
                    flash("An account with this email already exists.", "warning")
            elif role == "Client":
                if not user_exists(conn, "client", "mailCli", mail):
                    with conn.cursor() as cur:
                        cur.execute(
                            """
                            INSERT INTO client(nomCli, prenomCli, mailCli, telCli, mdpCli)
                            VALUES (%s, %s, %s, %s, %s);
                            """,
                            (name, firstname, mail, tel, hashed_password),
                        )
                    flash("Client account created successfully.", "success")
                    if 'user' in session:
                        return redirect(url_for("employe"))
                    else:
                        return redirect(url_for("client_login"))

                else:
                    flash("An account with this email already exists.", "warning")
        return redirect(url_for("show_error_page"))

# Login to account
@app.route("/login_account", methods=["POST"])
def login_account():

    if request.method == 'POST':
        mail = request.form['Email']
        mdp = request.form['Password']
        role = request.form["Role"]
        
        if not all([mail, mdp, role]):
            flash("All fields are required.", "danger")
            return redirect(url_for("shwo_error_page"))

        with db.connect() as conn:
            table_map = {
                "Manager": ("gerant", "mailGer", "mdpGer"),
                "Employe": ("employe", "mailEmp", "mdpEmp"),
                "Client": ("client", "mailCli", "mdpCli"),
            }
            if role in table_map:
                table, email_column, password_column = table_map[role]
                user = user_exists(conn, table, email_column, mail)
    # modify this later
                if user and password_ctx.verify(mdp, user[5]):
                    session['user'] = user
                    session['role'] = role
                    flash("Login successful.", "success")
                    if role == 'Manager':
                        return redirect(url_for("manager"))
                    elif role == 'Employe':
                        shop = request.form["shop"]
                        if int(shop) > 0:
                             with db.connect() as conn:
                                with conn.cursor() as cur:
                                    cur.execute(
                                        """
                                        SELECT idMag FROM travaille WHERE idEmp = %s AND idMag = %s;
                                        """,
                                        (int(session['user'][0]), int(shop)),
                                    )
                                    if cur.fetchall != None:
                                        session['shop'] = shop
                                    else:
                                        flash("Error we didn't find the shop.", "Danger")
                                        return redirect("show_error_page")
                                        
                        else:
                            from datetime import datetime
                            # Obtenir le jour actuel en anglais (par défaut)
                            jour_actuel = datetime.now().strftime("%A")

                            # Dictionnaire pour convertir les jours anglais en français
                            jours_conversion = {
                                "Monday": "Lundi",
                                "Tuesday": "Mardi",
                                "Wednesday": "Mercredi",
                                "Thursday": "Jeudi",
                                "Friday": "Vendredi",
                                "Saturday": "Samedi",
                                "Sunday": "Dimanche",
                            }
                            jour_actuel = jours_conversion[jour_actuel]
                            with db.connect() as conn:
                                print(jour_actuel)
                                print(user)
                                with conn.cursor() as cur:
                                    cur.execute(
                                    """
                                    SELECT idMag FROM travaille WHERE idEmp = %s AND jour = %s;
                                    """,
                                    (int(user[0]), jour_actuel),)
                                    result = cur.fetchone()  # Récupérer le premier résultat

                                    if result is not None:  # Si un magasin est trouvé pour cet employé et ce jour
                                        session['shop'] = result[0]  # Récupérer l'ID du magasin et l'ajouter à la session
                                    else:
                                        flash("Error: we didn't find the shop.", "danger")
                                        return redirect("show_error_page")  # Rediriger vers une page d'erreur si aucun magasin n'est trouvé page")
                        return redirect(url_for("employe"))
                    else:
                        return redirect(url_for("client"))
                else:
                    flash("Invalid email or password.", "danger")
                    return redirect(url_for("show_error_page"))
            else:
                flash("Invalid role selected or shop.", "warning")
                return redirect(url_for("show_error_page"))
            
# Manager page
@app.route("/manager")
def manager():
    if 'user' not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for("gerant_login"))

    try:
        with db.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT idComp, nomComp, stock, prixUnit
                    FROM vend
                    NATURAL JOIN magasin
                    NATURAL JOIN composant
                    WHERE idGer = %s;
                    """,
                    (int(session['user'][0]),),
                )
                products = cur.fetchall()
            return render_template("profile.html", composants=products)
    except Exception as e:
        flash(f"Error loading manager page: {e}", "danger")
        return redirect(url_for("show_error_page"))

# More routes can follow similar patterns for product management, error handling, etc.
# Add a new product
@app.route('/add_product', methods=['POST'])
def add_product():
    if 'user' not in session or session['role'] != "Manager":
        flash("Unauthorized action.", "warning")
        return redirect(url_for("login"))

    name = request.form.get('name').capitalize()
    description = request.form.get('description')
    brand = request.form.get('brand').upper()
    price = request.form.get('price')
    stock = request.form.get('stock')

    if not name or not description or not brand:
        flash("All fields are required.", "warning")
        return redirect(url_for("manager"))

    try:
        print('hh')
        price = float(price)
        stock = int(stock)
        if price <= 0 or stock < 0:
            raise ValueError("Invalid price or stock values.")

        with db.connect() as conn:
            with conn.cursor() as cur:
                # Insert into composant
                cur.execute(
                    """
                    INSERT INTO composant(nomComp, descriptionComp, marqueComp) 
                    VALUES (%s, %s, %s) RETURNING idComp;
                    """,
                    (name, description, brand)
                )
                idComp = cur.fetchone()[0]
                print("idComp = ", idComp)
                # Link to the manager's shop in vend
                cur.execute(
                    """
                    INSERT INTO vend(idMag, idComp, prixUnit, stock)
                    VALUES (
                        (SELECT idMag FROM magasin WHERE idGer = %s),
                        %s, %s, %s
                    ) returning idMag;
                    """,
                    (int(session['user'][0]), int(idComp), float(price), int(stock))
                )
                vend = cur.fetchall()
                print("vend = ", vend)
            flash("Product added successfully.", "success")
        return redirect(url_for("manager"))
    except Exception as e:
        print("gg")
        flash(f"Error adding product: {e}", "danger")
        return redirect(url_for("show_error_page"))


# View a specific product
@app.route("/product_<int:id_comp>")
def product(id_comp):
    if 'user' not in session:
        flash("You must be logged in to view this page.", "warning")
        return redirect(url_for("login"))

    try:
        with db.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT composant.idComp, nomComp, marqueComp, descriptionComp, prixUnit, stock
                    FROM vend
                    NATURAL JOIN composant 
                    NATURAL JOIN magasin
                    WHERE composant.idComp = %s AND idGer = %s;
                    """,
                    (id_comp, session['user'][0])
                )
                product = cur.fetchone()
        if product:
            return render_template("produit.html", product=product)
        flash("Product not found.", "warning")
    except Exception as e:
        flash(f"Error loading product: {e}", "danger")
    return redirect(url_for("show_error_page"))


# Update a product
@app.route("/update_product", methods=["POST"])
def update_product():
    if 'user' not in session or session['role'] != "Manager":
        flash("Unauthorized action.", "warning")
        return redirect(url_for("login"))

    id_comp = request.form.get("product_id")
    name = request.form.get("product_name")
    description = request.form.get("product_description")
    brand = request.form.get("product_brand")
    price = request.form.get("product_price")
    stock = request.form.get("product_stock")

    if not all([id_comp, name, description, brand, price, stock]):
        flash("All fields are required.", "warning")
        return redirect(url_for("manager"))

    try:
        price = float(price)
        stock = int(stock)
        if price <= 0 or stock < 0:
            raise ValueError("Invalid price or stock values.")

        with db.connect() as conn:
            with conn.cursor() as cur:
                # Update composant
                cur.execute(
                    """
                    UPDATE composant
                    SET nomComp = %s, descriptionComp = %s, marqueComp = %s
                    WHERE idComp = %s;
                    """,
                    (name, description, brand, id_comp)
                )
                # Update vend
                cur.execute(
                    """
                    UPDATE vend
                    SET stock = %s, prixUnit = %s
                    WHERE idComp = %s AND idMag = (
                        SELECT idMag FROM magasin WHERE idGer = %s
                    );
                    """,
                    (stock, price, id_comp, session['user'][0])
                )
            flash("Product updated successfully.", "success")
        return redirect(url_for("manager"))
    except Exception as e:
        flash(f"Error updating product: {e}", "danger")
        return redirect(url_for("product", id_comp=id_comp))


# Delete a product
@app.route("/remove_product", methods=["GET"])
def remove_product():
    if 'user' not in session or session['role'] != "Manager":
        flash("Unauthorized action.", "warning")
        return redirect(url_for("login"))

    id_comp = request.args.get("product_id")
    if not id_comp:
        flash("Invalid product ID.", "warning")
        return redirect(url_for("manager"))

    try:
        with db.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DELETE FROM vend
                    USING magasin
                    WHERE vend.idComp = %s AND magasin.idGer = %s;
                    """,
                    (id_comp, session['user'][0])
                )
            flash("Product removed successfully.", "success")
        return redirect(url_for("manager"))
    except Exception as e:
        flash(f"Error removing product: {e}", "danger")
        return redirect(url_for("manager"))


# Shop view
@app.route("/shop")
def shop():
    if 'user' not in session:
        flash("Please log in to view this page.", "warning")
        return redirect(url_for("login"))

    try:
        with db.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT *
                    FROM magasin NATURAL JOIN gerant
                    WHERE idGer = %s;
                    """,
                    (session['user'][0],)
                )
                shops = cur.fetchone()
                print(shops)
        return render_template("magasin.html", shop=shops)
    except Exception as e:
        flash(f"Error loading shops: {e}", "danger")
        return redirect(url_for("manager"))


@app.route('/update_shop', methods=['POST'])

def update_shop():
    try:
        # Extract form data
        nomMag = request.form['nomMag']
        adresseMag = request.form['adresseMag']
        telMag = request.form['telMag']
        nomGerant = request.form['nomGerant']
        prenomGerant = request.form['prenomGerant']
        emailGerant = request.form['emailGerant']
        telGerant = request.form['telGerant']
        magasin_id = request.form['idMag']
        gerant_id = session['user'][0]  # Replace with dynamic ID logic

        # Input length constraints
        if not (2 <= len(nomMag) <= 50):
            flash("Store name must be between 2 and 50 characters.", "error")
            return redirect(url_for('shop'))
        if not (5 <= len(adresseMag) <= 50):
            flash("Store address must be between 5 and 100 characters.", "error")
            return redirect(url_for('shop'))
        if not is_valid_phone_number(telMag):
            flash("Store phone number must contain only numbers and be 10-16 digits long.", "error")
            return redirect(url_for('shop'))
        if not (2 <= len(nomGerant) <= 50):
            flash("Manager name must be between 2 and 50 characters.", "error")
            return redirect(url_for('shop'))
        if not (2 <= len(prenomGerant) <= 50):
            flash("Manager first name must be between 2 and 50 characters.", "error")
            return redirect(url_for('shop'))
        if not is_valid_phone_number(telGerant):
            flash("Manager phone number must contain only numbers and be 10-16 digits long.", "error")
            return redirect(url_for('shop'))
        if not (5 <= len(emailGerant) <= 50) or "@" not in emailGerant:
            flash("Manager email must be a valid email address and between 5 and 100 characters.", "error")
            return redirect(url_for('shop'))
        
        if not gerant_id or not magasin_id:
            flash("Missing manager or store ID.", "error")
            return redirect(url_for('shop'))

        # Database update
        with  db.connect() as conn:
            with conn.cursor() as cur:
                # Update Magasin table
                cur.execute(
                    """
                    UPDATE magasin
                    SET nomMag = %s,
                        adresseMag = %s,
                        telMag = %s
                    WHERE idMag = %s
                    """,
                    (nomMag, adresseMag, telMag, int(magasin_id))
                )

                # Update Gerant table
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE gerant
                    SET nomGer = %s,
                        prenomGer = %s,
                        mailGer = %s,
                        telGer = %s
                    WHERE idGer = %s
                    """,
                    (nomGerant, prenomGerant, emailGerant, telGerant, int(gerant_id))
                )

            flash("Store and Manager information updated successfully.", "success")
            return redirect(url_for('shop'))

    except Exception as e:
        # Rollback on failure
        db.rollback()
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('show_error_page'))


# Employee shifts view
@app.route("/employeshifts")
def employeshifts():
    if 'user' not in session or session['role'] != "Manager":
        flash("Unauthorized action.", "warning")
        return redirect(url_for("login"))
    # Example data fetch for shifts (adjust query as per your database schema)
    try:
        with db.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                SELECT 
                e.idEmp AS employee_id,
                e.nomEmp AS employee_name,
                e.prenomEmp AS employee_first_name,
                e.mailEmp AS employee_email,
                e.telEmp AS employee_phone,
                ARRAY_AGG(t.jour ORDER BY t.jour) AS availability_days
                FROM 
                employe e
                JOIN 
                travaille t ON e.idEmp = t.idEmp
                WHERE 
                t.idMag = %s
                GROUP BY 
                e.idEmp, e.nomEmp, e.prenomEmp, e.mailEmp, e.telEmp
                ORDER BY 
                    e.idEmp;

                    """,
                    (int(session['user'][0]),)
                )
            
                shifts = cur.fetchall()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT 
                    e.idEmp AS employee_id,
                    e.nomEmp AS employee_name,
                    e.prenomEmp AS employee_first_name,
                    e.mailEmp AS employee_email,
                    e.telEmp AS employee_phone,
                    ARRAY_AGG(t.jour ORDER BY t.jour) AS availability_days
                    FROM 
                    employe e
                    LEFT JOIN 
                    travaille t ON e.idEmp = t.idEmp
                    GROUP BY 
                    e.idEmp, e.nomEmp, e.prenomEmp, e.mailEmp, e.telEmp
                    ORDER BY 
                    e.idEmp;
                    """,
                    (int(session['user'][0]),)
                )
                available = cur.fetchall()
            
        return render_template("shiftemployee.html", shifts=shifts, available=available)
    except Exception as e:
        flash(f"Error loading shifts: {e}", "danger")
        return redirect(url_for("show_error_page"))



@app.route('/add_work_days', methods=['POST'])
def add_work_days():
    try:
        days = request.form.getlist('days')  # Extract the list of days from form data (checkboxes)
        idEmp = request.form['idEmp']  # Extract the employee ID
        idGerant = int(session['user'][0])  # Get the current manager's ID from the session
        
        print(f"Selected days: {days}")  # Debugging: check the received days list
        
        # Define days in French
        days_in_french = ["Dimanche", "Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"]

        # Connect to the database
        with db.connect() as conn:
            idMag = find_magasin_by_gerant(conn, idGerant)[0]  # Find the magasin ID for the gerant
            if not idMag:
                flash("Magasin not found for the current manager.", "warning")
                return redirect(url_for('employeshifts'))

            for day in days:
                if day not in days_in_french:
                    flash(f"An error occurred: '{day}' is not a valid day", "danger")
                    return redirect(url_for('show_error_page'))
                
                try:
                    with conn.cursor() as cur:
                        # Insert the record for each valid day
                        cur.execute(
                            """
                            INSERT INTO travaille (idMag, idEmp, jour)
                            VALUES (%s, %s, %s)
                            """,
                            (int(idMag), int(idEmp), day)
                        )
                    print(f"Inserted day: {day}")  # Debugging: check which day was inserted
                except Exception as e:
                    # Handle the specific database error (duplicate entry or other issue)
                    print(f"Error: {e}")
                    conn.rollback()  # Roll back the transaction on duplicate entry
                    flash(f"An error occurred: the day '{day}' already exists for this employee.", "danger")
                    return redirect(url_for('show_error_page'))

        flash("Work days added successfully.", "success")
        return redirect(url_for('employeshifts'))

    except Exception as e:
        flash(f"An error occurred: {str(e)}", "danger")
        return redirect(url_for('show_error_page'))


@app.route('/remove_work_days', methods=['POST'])
def remove_work_days():
    try:
        # Extract the list of days from form data (checkboxes)
        days = request.form.getlist('days')
        idEmp = request.form['idEmp']  # Extract the employee ID
        idGerant = int(session['user'][0])  # Get the current manager's ID from the session
        # Define days in French
        days_in_french = ["Dimanche", "Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"]

        # Validate if at least one day is selected
        if not days:
            flash("No days selected. Please select at least one day to remove.", "warning")
            return redirect(url_for('employeshifts'))

        # Connect to the database
        with db.connect() as conn:
            # Find the magasin ID for the gerant
            idMag = find_magasin_by_gerant(conn, idGerant)[0]
            if not idMag:
                flash("Magasin not found for the current manager.", "warning")
                return redirect(url_for('employeshifts'))

            # Loop through the selected days and delete the corresponding records
            for day in days:
                if day not in days_in_french:
                    flash(f"An error occurred: '{day}' is not a valid day", "danger")
                    return redirect(url_for('show_error_page'))
                
                try:
                    with conn.cursor() as cur:
                        # Delete the record for each valid day
                        cur.execute(
                            """
                            DELETE FROM travaille
                            WHERE idMag = %s AND idEmp = %s AND jour = %s
                            """,
                            (int(idMag), int(idEmp), day)
                        )
                        print(f"Deleted day: {day}")  # Debugging: check which day was deleted
                except Exception as e:
                    conn.rollback()
                    # Handle specific errors, like if the entry does not exist
                    print(f"Error: {e}")
                    flash(f"An error occurred: Unable to delete the day '{day}' for this employee.", "danger")
                    return redirect(url_for('show_error_page'))

        # If everything is successful
        flash("Work days removed successfully.", "success")
        return redirect(url_for('employeshifts'))

    except Exception as e:
        flash(f"An error occurred: {str(e)}", "danger")
        return redirect(url_for('show_error_page'))


@app.route('/search_product', methods=['GET'])
def search_product():
    product_name = request.args.get('product', '')  # Get the product name from the query string

    if product_name:
        # Connect to the database
        with db.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(f"SELECT idComp, nomComp, stock, prixUnit FROM composant NATURAL JOIN magasin NATURAL JOIN vend  WHERE lower(nomComp) LIKE '%{product_name.lower()}%' OR lower(marqueComp) LIKE '%{product_name.lower()}%'")  # Use ILIKE for case-insensitive search
                products = cur.fetchall()  # Fetch the results    
            
            # Return the search results to the template
            return render_template('searchproducts.html', products=products, product=product_name)
    else:
        # If no product is entered, just render the template without results
        return render_template('searchproducts.html', products=[], product=product_name)

@app.route('/allproduct', methods=['GET'])
def all_products():
    if 'user' in session:    
        try:
            with db.connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT idComp, nomComp, stock, prixUnit
                        FROM vend
                        NATURAL JOIN magasin
                        NATURAL JOIN composant
                        WHERE idGer = %s;
                        """,
                        (int(session['user'][0]),),
                    )
                    products = cur.fetchall()
                return render_template("searchproducts.html", products=products)
        except Exception as e:
            flash(f"Error loading manager page: {e}", "danger")
            return redirect(url_for("show_error_page"))
    else:
        flash(f"Error you're not logged in", "danger")
        return redirect(url_for("show_error_page"))

@app.route('/statistique')
def statistic():
    if 'user' in session:
        try:
            idGer = int(session['user'][0])  # Ensure `idGer` is an integer.
            with db.connect() as conn:
                # Query for product details
                query_products = """
                    SELECT 
                        c.idComp, c.nomComp, c.descriptionComp, c.marqueComp, 
                        SUM(df.quantite) AS total_quantity, 
                        SUM(df.reductionComp * df.quantite) AS total_price
                    FROM detailfact df
                     JOIN facture f ON df.idFact = f.idFact
                     JOIN magasin m ON f.idMag = m.idMag
                     JOIN composant c ON df.idComp = c.idComp
                    WHERE m.idGer = %s
                    GROUP BY c.idComp, c.nomComp, c.descriptionComp, c.marqueComp;
                """
                with conn.cursor() as cur:
                    cur.execute(query_products, (idGer,))
                    products = cur.fetchall()

                # Query for total sales revenue
                query_total = """
                        SELECT sum(quantite * reductionComp)
                        FROM detailfact
                        NATURAL JOIN magasin 
                        NATURAL JOIN composant NATURAL JOIN facture
                        WHERE idGer = %s;
                """
                with conn.cursor() as cur:
                    cur.execute(query_total, (idGer,))
                    total = cur.fetchone()[0]

                # Query for invoice count
                query_facture_count = """
                    SELECT 
                        COUNT(*) AS total_factures
                    FROM facture f
                    JOIN magasin m ON f.idMag = m.idMag
                    WHERE m.idGer = %s;
                """
                with conn.cursor() as cur:
                    cur.execute(query_facture_count, (idGer,))
                    facture = cur.fetchone()[0]
                print(facture)
            # Render template
            return render_template(
                "statistique.html", 
                products=products, 
                total=total or 0,  # Default to 0 if None
                facture=facture or 0  # Default to 0 if None
            )

        except Exception as e:
            # Log the error for debugging (use a logging framework in production)
            flash(f"Error loading statistic page: {str(e)}", "danger")
            return redirect(url_for("show_error_page"))
    else:
        flash("Error: You're not logged in", "danger")
        return redirect(url_for("show_error_page"))

@app.route("/employe")
def employe():
    if 'user' in session and 'role' in session and 'shop' in session:
        print(session['shop'])
        if session['role'] == 'Employe':
            try:
                with db.connect() as conn:
                    try:
                        with conn.cursor() as cur:
                            # Query for factures
                            cur.execute(
                                "SELECT idEmp, idFact, nomCli, idCli, prenomCli, dateAchat, COUNT(DISTINCT idComp) as nbproduct  FROM facture NATURAL JOIN client NATURAL LEFT  JOIN detailfact WHERE idMag = %s GROUP BY idFact, nomCli, idCli, prenomCli, dateAchat, idEmp;",
                                (int(session['shop']), )
                            )
                            factures = cur.fetchall()
                    except Exception as e:
                        flash(f"Error fetching factures: {str(e)}", "error")
                        return redirect(url_for("show_error_page"))

                    try:
                        with conn.cursor() as cur:
                            # Query for clients
                            cur.execute("SELECT * FROM client")
                            clients = cur.fetchall()
                    except Exception as e:
                        flash(f"Error fetching clients: {str(e)}", "error")
                        return redirect(url_for("show_error_page"))

                # Render the template if no errors occurred
                return render_template("employe.html", clients=clients, factures=factures)

            except Exception as e:
                flash(f"Database connection error: {str(e)}", "error")
                return redirect(url_for("show_error_page"))
        else:
            flash("You are not authorized to access this page.", "error")
            return redirect(url_for("show_error_page"))
    else:
        flash("You must be logged in to access this page.", "error")
        return redirect(url_for("employe_login"))
 
@app.route("/add_facture" , methods=["POST"])
def add_facture():
    ima = datetime.date.today()
    print(ima)
    idCli = request.form['idCli']  # Extract the employee ID
    if 'user' in session and 'role' in session and 'shop' in session:
        if session['role'] == 'Employe':
            try:
                with db.connect() as conn:
                    try:
                        
                        with conn.cursor() as cur:
                            # Query for factures
# à modify                  
                            query = "INSERT INTO facture (idEmp, idMag, idCli, dateAchat) VALUES ( %s, %s, %s, %s);"
                            cur.execute(
                                query,
                                (int(session['user'][0]), int(session['shop']), int(idCli), ima,)
                            )
                            print("ca marche \n")
                    except Exception as e:
                        flash(f"Error fetching factures: {str(e)}", "error")
                        return redirect(url_for("show_error_page"))

                    return redirect(url_for("employe"))

            except Exception as e:
                flash(f"Database connection error: {str(e)}", "error")
                return redirect(url_for("show_error_page"))
        else:
            flash("You are not authorized to access this page.", "error")
            return redirect(url_for("show_error_page"))
    else:
        flash("You must be logged in to access this page.", "error")
        return redirect(url_for("employe_login"))
    
@app.route("/employe_personelle")
def employe_personelle():
    return render_template("info_emp.html")
@app.route("/facture_<int:id_fact>")
def facture(id_fact):
    if 'user' not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for("employe_login"))

    try:
        with db.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT composant.idComp, composant.nomComp, quantite, reductionComp
                    FROM detailfact NATURAL JOIN composant
                    NATURAL JOIN facture
                    WHERE idFact = %s;
                    """,
                    (int(id_fact),),
                )
                products = cur.fetchall()
                
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT composant.idComp, composant.nomComp, prixUnit
                    FROM vend NATURAL JOIN composant 
                    WHERE idMag = %s;
                    """,
                    (int(session['shop']),),
                )
                product_choice = cur.fetchall()
                for elem in products:
                    for elem1 in product_choice:
                        if elem[0] == elem1[0]:
                            product_choice.remove(elem1)
            return render_template("facture.html", composants=products, idfact=id_fact, product_choice = product_choice)
    except Exception as e:
        flash(f"Error loading manager page: {e}", "danger")
        return redirect(url_for("show_error_page"))



@app.route('/add_composantfacture', methods=["POST"])
def add_composant_fact():
    if 'user' in session:  # Vérifiez si l'utilisateur est connecté
        try:
            # Récupérer les données depuis la requête POST
            id_fact = request.form.get("idFact")
            id_comp = request.form.get("idComp")
            quantite = request.form.get("quantite")

            # Valider les entrées
            if not (id_fact and id_comp and quantite):
                flash("all data are required.", "danger")
                return redirect(url_for("show_error_page"))

            id_fact = int(id_fact)
            id_comp = int(id_comp)
            quantite = int(quantite)

            # Opérations avec la base de données
            with db.connect() as conn:
                try:
                    with conn.cursor() as cur:
                        # Vérifier le stock et mettre à jour
                        cur.execute(
                            """
                            SELECT stock FROM vend 
                            WHERE idMag = %s AND idComp = %s;
                            """,
                            (int(session['shop']), id_comp),
                        )
                        stock = cur.fetchone()

                        if not stock or int(stock[0]) < quantite:
                            flash("Quantite insufficiante in  stock.", "danger")
                            return redirect(url_for("show_error_page"))

                        # Réduire le stock
                        cur.execute(
                            """
                            UPDATE vend
                            SET stock = stock - %s
                            WHERE idMag = %s AND idComp = %s;
                            """,
                            (quantite, int(session['shop']), id_comp),
                        )

                        # Récupérer le prix unitaire
                        cur.execute(
                            """
                            SELECT prixUnit FROM vend 
                            WHERE idMag = %s AND idComp = %s;
                            """,
                            (int(session['shop']), id_comp),
                        )
                        prix = cur.fetchone()[0]

                        # Insérer dans detailfact
                        cur.execute(
                            """
                            INSERT INTO detailfact (idFact, idComp, quantite, reductionComp)
                            VALUES (%s, %s, %s, %s);
                            """,
                            (id_fact, id_comp, quantite, int(prix)),
                        )
                    flash("Composant added to the bill.", "success")
                    return redirect(url_for("employe"))

                except Exception as e:
                    flash(f"Erreur : {e}", "danger")
                    return redirect(url_for("show_error_page"))

        except ValueError as ve:
            flash("Invalid data.", "danger")
            return redirect(url_for("show_error_page"))

        except Exception as e:
            flash(f"Erreur : {e}", "danger")
            return redirect(url_for("show_error_page"))

    else:
        flash("You need to ligin as employe to add composant to the bills.", "danger")
        return redirect(url_for("employe_login"))

@app.route("/factureproduct_<int:id_comp>_<int:id_fact>")
def factureproduct(id_comp, id_fact):
    if 'user' not in session:
        flash("You must be logged in to view this page.", "warning")
        return redirect(url_for("employe_login"))

    try:
        with db.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT composant.idComp, composant.nomComp, composant.descriptionComp, marqueComp, quantite, reductionComp
                    FROM detailfact NATURAL JOIN composant
                    NATURAL JOIN facture
                    WHERE idFact = %s and idComp = %s;
                    """,
                    (int(id_fact), int(id_comp),)
                )
                product = cur.fetchone()
        if product:
            return render_template("produit.html", product=product)
        flash("Product not found.", "warning")
    except Exception as e:
        flash(f"Error loading product: {e}", "danger")
    return redirect(url_for("show_error_page"))


@app.route("/employe_update", methods=["POST"])
def employe_update():
    try:
        # Extract form data
        idEmp = request.form["idEmp"]
        nomEmp = request.form['nomEmp']
        prenomEmp = request.form['prenomEmp']
        mailEmp = request.form['mailEmp']
        telEmp = request.form['telEmp']
        
        # Input length constraints
        if not (2 <= len(nomEmp) <= 50):
            flash("Store name must be between 2 and 50 characters.", "error")
            return redirect(url_for('employe'))
        if not is_valid_phone_number(telEmp):
            flash("Store phone number must contain only numbers and be 10-16 digits long.", "error")
            return redirect(url_for('employe'))
        if not (2 <= len(prenomEmp) <= 50):
            flash("first name must be between 2 and 50 characters.", "error")
            return redirect(url_for('employe'))
        if not (5 <= len(mailEmp) <= 50) or "@" not in mailEmp:
            flash(" email must be a valid email address and between 5 and 100 characters.", "error")
            return redirect(url_for('employe'))
        # Database update
        with db.connect() as conn:
            with conn.cursor() as cur:
                # Update employe table
                cur.execute(
                    """
                    UPDATE employe
                    SET nomEmp = %s,
                        prenomEmp = %s,
                        telEmp = %s, 
                        mailEmp = %s
                    WHERE idEmp = %s 
                    """,
                    (nomEmp, prenomEmp, '+' + telEmp, mailEmp, int(idEmp))
                )
            with conn.cursor() as cur:
                # Update employe table
                cur.execute(
                    """
                    select * from employe 
                    WHERE idEmp = %s 
                    """,
                    (int(idEmp),)
                )
                session['user'] = cur.fetchone()
            flash("employe information updated successfully.", "success")
            return redirect(url_for('employe'))

    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('show_error_page'))



@app.route("/client")
def client():
    if 'user' not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for("client_login"))

    try:
        with db.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT * FROM magasin
                    """
                )
                magasins = cur.fetchall()
            with conn.cursor() as cur:
                            # Query for factures
                cur.execute(
                        "SELECT idEmp, idFact, nomCli, idCli, prenomCli, dateAchat, COUNT(DISTINCT idComp) as nbproduct  FROM facture NATURAL JOIN client NATURAL LEFT  JOIN detailfact WHERE idCli = %s GROUP BY idFact, nomCli, idCli, prenomCli, dateAchat, idEmp;",
                        (int(session['user'][0]), )
                )
                factures = cur.fetchall()
            with conn.cursor() as cur:
                            # Query for factures
                cur.execute(
                "SELECT * from projet where idCli = %s ORDER BY idProj;"
                ,(int(session['user'][0]), )
                )
                projects = cur.fetchall()
                            
            
                            
            return render_template("client.html", magasins=magasins, factures=factures, projects=projects)
    except Exception as e:
        flash(f"Error loading client page: {e}", "danger")
        return redirect(url_for("show_error_page"))



@app.route("/magasin_<int:idmag>")
def magasin_produit(idmag):

    try:
        with db.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT composant.idComp, composant.nomComp, stock, prixUnit
                    FROM vend NATURAL JOIN composant
                    NATURAL JOIN magasin
                    WHERE idMag = %s;
                    """,
                    (int(idmag),)
                )
                products = cur.fetchall()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT *
                    FROM magasin NATURAL JOIN gerant
                    WHERE idMag = %s;
                    """,
                    (int(idmag),)
                     )
                shops = cur.fetchone()
            return render_template("magasin_produit.html", products=products, shop= shops)
    except Exception as e:
        flash(f"Error loading client page: {e}", "danger")
        return redirect(url_for("show_error_page"))




@app.route("/product_magasin_<int:id_comp>_<int:idmag>")
def product_magasin(id_comp, idmag):

    try:
        with db.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT composant.idComp, nomComp, marqueComp, descriptionComp, prixUnit, stock
                    FROM vend
                    NATURAL JOIN composant 
                    NATURAL JOIN magasin
                    WHERE composant.idComp = %s AND idMag = %s;
                    """,
                    (int(id_comp), int(idmag))
                )
                product = cur.fetchone()
        if product:
            return render_template("produit.html", product=product)
        flash("Product not found.", "warning")
    except Exception as e:
        flash(f"Error loading product: {e}", "danger")
    return redirect(url_for("show_error_page"))



@app.route('/search_product_magasin', methods=['GET'])
def search_product_magasin():
    product_name = request.args.get('product', '')  # Get the product name from the query string
    if product_name:
        # Connect to the database
        with db.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(f"SELECT idComp, nomComp, marqueComp, stock, prixUnit, nomMag FROM composant NATURAL JOIN magasin NATURAL JOIN vend  WHERE lower(nomComp) LIKE '%{product_name.lower()}%' OR lower(marqueComp) LIKE '%{product_name.lower()}%'")  # Use ILIKE for case-insensitive search
                products = cur.fetchall()  # Fetch the results    

            # Return the search results to the template
            return render_template('searchproducts_magasin.html', products=products, product=product_name)
    else:
        # If no product is entered, just render the template without results
        return render_template('searchproducts.html', products=[], product=product_name)



@app.route("/facture_client_<int:id_fact>")
def facture_client(id_fact):
    if 'user' not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for("client_login"))

    try:
        with db.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT composant.idComp, composant.nomComp, quantite, reductionComp, nomMag
                    FROM detailfact NATURAL JOIN composant
                    NATURAL JOIN facture NATURAL JOIN magasin
                    WHERE idFact = %s;
                    """,
                    (int(id_fact),),
                )
                products = cur.fetchall()
            return render_template("facture_client.html", composants=products)
    except Exception as e:
        flash(f"Error loading manager page: {e}", "danger")
        return redirect(url_for("show_error_page"))



@app.route("/project_<int:idproj>")
def projet(idproj):
    if 'user' not in session:
        flash("You must be logged in to view this page.", "warning")
        return redirect(url_for("client_login"))

    try:
        with db.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT composant.idComp, nomComp, marqueComp, descriptionComp
                    FROM composant 
                    NATURAL JOIN contient
                    WHERE idProj = %s;
                    """,
                    (int(idproj),)
                )
                productproject = cur.fetchall()
            with conn.cursor() as cur:
                # Exécuter la requête pour obtenir les composants, prix et magasins
                cur.execute(
                    """
                    SELECT composant.idComp, 
                        composant.nomComp , composant.descriptionComp, composant.marqueComp,
                        vend.prixUnit,
                        magasin.nomMag
                    FROM 
                        contient
                    NATURAL JOIN composant
                    natural join 
                    magasin NATURAL JOIN vend
                    WHERE 
                        contient.idProj = %s 
                    GROUP BY composant.idComp, 
                        composant.nomComp , composant.descriptionComp, composant.marqueComp,
                        vend.prixUnit,
                        magasin.nomMag 
                        order by prixUnit;
                    """,
                    (int(idproj),)
                )
                components = cur.fetchall()
        return render_template("projet.html", products=components, productprojects=productproject, idproj=idproj)
    except Exception as e:
        flash(f"Error loading product: {e}", "danger")
    return redirect(url_for("show_error_page"))    


@app.route("/add_remove_component_<int:idproj>")
def add_remove_component(idproj):
    return render_template("add_remove_components.html", idProj = idproj)



@app.route("/addproject", methods=["POST"])
def add_project():
    if 'user' not in session:
        flash("You must be logged in to view this page.", "warning")
        return redirect(url_for("client_login"))

    try:
        # Get data from the form
        nomproj = request.form["nomProj"]

        # Database operation
        with db.connect() as conn:
            with conn.cursor() as cur:
                # Insert data into the contient table
                cur.execute(
                    """
                    INSERT INTO projet (idCli, nomProj)
                    VALUES (%s, %s)
                    """,
                    (int(session['user'][0]),nomproj,)
                )
        flash("project added successfully.", "success")
        return redirect(url_for("client"))
    except KeyError:
        flash("Invalid input. Please provide both component and project IDs.", "danger")
    except Exception as e:
        flash(f"An error occurred: {e}", "danger")
    return redirect(url_for("show_error_page"))




@app.route("/addcomponent", methods=["POST"])
def add_component():
    if 'user' not in session:
        flash("You must be logged in to view this page.", "warning")
        return redirect(url_for("client_login"))

    try:
        # Get data from the form
        idcomp = int(request.form["idComp"])
        idproj = int(request.form["idProj"])
        quantite = int(request.form["quantite"])

        # Database operation
        with db.connect() as conn:
            with conn.cursor() as cur:
                # Insert data into the contient table
                cur.execute(
                    """
                    INSERT INTO contient (idComp, idProj, quantite)
                    VALUES (%s, %s, %s)
                    """,
                    (int(idcomp), int(idproj), int(quantite),)
                )
        flash("Component added successfully.", "success")
        return redirect(url_for("client"))
    except KeyError:
        flash("Invalid input. Please provide both component and project IDs.", "danger")
    except Exception as e:
        flash(f"An error occurred: {e}", "danger")
    return redirect(url_for("show_error_page"))

@app.route("/removecomponent", methods=["POST"])
def remove_component():
    if 'user' not in session:
        flash("You must be logged in to view this page.", "warning")
        return redirect(url_for("client_login"))

    try:
        
        # Get data from the form
        idcomp = int(request.form["idComp"])
        idproj = int(request.form["idProj"])
        print(idcomp, idproj)
        # Database operation
        with db.connect() as conn:
            with conn.cursor() as cur:
                # Ensure proper SQL query with WHERE clause
                cur.execute(
                    """
                    DELETE FROM contient 
                    WHERE idComp = %s AND idProj = %s
                    """,
                    (idcomp, idproj,)
                )

        flash("Component removed successfully.", "success")
        return redirect(url_for("client"))
    except KeyError:
        flash("Invalid input. Please provide both component and project IDs.", "danger")
    except Exception as e:
        flash(f"An error occurred: {e}", "danger")
    return redirect(url_for("show_error_page"))


@app.route("/removeproject", methods=["POST"])
def removeproject():
    if 'user' not in session:
        flash("You must be logged in to view this page.", "warning")
        return redirect(url_for("client_login"))

    try:
        
        # Get data from the form
        idproj = int(request.form["idProj"])
        # Database operation
        with db.connect() as conn:
            with conn.cursor() as cur:
                # Ensure proper SQL query with WHERE clause
                cur.execute(
                    """
                    DELETE FROM projet 
                    WHERE idProj = %s;
                    """,
                    (idproj,)
                )

        flash("Project removed successfully.", "success")
        return redirect(url_for("client"))
    except KeyError:
        flash("Invalid input. Please provide both component and project IDs.", "danger")
    except Exception as e:
        flash(f"An error occurred: {e}", "danger")
    return redirect(url_for("show_error_page"))


@app.route("/client_personnelle")
def clper():
    return render_template("client_personnelle.html")

@app.route("/client_update", methods=["POST"])
def client_update():
    try:
        # Extract form data
        idEmp = request.form["idEmp"]
        nomEmp = request.form['nomEmp']
        prenomEmp = request.form['prenomEmp']
        mailEmp = request.form['mailEmp']
        telEmp = request.form['telEmp']
        
        # Input length constraints
        if not (2 <= len(nomEmp) <= 50):
            flash("Store name must be between 2 and 50 characters.", "error")
            return redirect(url_for('employe'))
        if not is_valid_phone_number(telEmp):
            flash("Store phone number must contain only numbers and be 10-16 digits long.", "error")
            return redirect(url_for('employe'))
        if not (2 <= len(prenomEmp) <= 50):
            flash("first name must be between 2 and 50 characters.", "error")
            return redirect(url_for('employe'))
        if not (5 <= len(mailEmp) <= 50) or "@" not in mailEmp:
            flash(" email must be a valid email address and between 5 and 100 characters.", "error")
            return redirect(url_for('employe'))
        # Database update
        with db.connect() as conn:
            with conn.cursor() as cur:
                # Update employe table
                cur.execute(
                    """
                    UPDATE client
                    SET nomCli = %s,
                        prenomCli = %s,
                        telCli = %s, 
                        mailCli = %s
                    WHERE idCli = %s 

                    """,
                    (nomEmp, prenomEmp, '+' + telEmp, mailEmp, int(idEmp))
                )
            with conn.cursor() as cur:
                cur.execute(
                        """
                        select * from client
                        WHERE idCli = %s 
                        
                        """,
                        (int(idEmp),)
                    )
                session['user'] = cur.fetchone()
            flash("Client information updated successfully.", "success")
            return redirect(url_for('client'))

    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('show_error_page'))



@app.route("/catalogue")
def catalogue():
    try:
        with db.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT * FROM magasin
                    """
                )
                magasins = cur.fetchall()
            return render_template("catalogue.html", magasins=magasins)
    except Exception as e:
        flash(f"Error loading client page: {e}", "danger")
        return redirect(url_for("show_error_page"))




@app.route("/")
def acceuil():
    return render_template("acceuil.html")

@app.route("/logout")
def logout():
    if 'user' in session:
        session.pop("user")
    if 'role' in session:
        if session['role'] == "Manager":
            session.pop("role")
            return redirect("/")
        elif session['role'] == "Employe":
            session.pop("shop")
            session.pop("role")
            return redirect("/")
        else:
            session.pop("role")
            return redirect("/")
if __name__ == '__main__':
    app.run(debug=True)
