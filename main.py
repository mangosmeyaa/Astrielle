from flask import Flask, render_template, request, flash, redirect, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

import pymysql

from dynaconf import Dynaconf


app = Flask(__name__)

config = Dynaconf(settings_file=["settings.toml"])

app.secret_key = config.secret_key

login_manager = LoginManager(app)
login_manager.loginview ='/login'
class User:
  is_authenticated = True
  is_active = True
  is_anonymous = False

  def __init__(self, result):
      self.name = result['Name']
      self.email = result['Email']
      self.address = result['Address']
      self.id = result['ID']

def get_id(self):
    return str(self.id)

@login_manager.user_loader
def load_user(user_id):

  connection = connect_db()
  cursor = connection.cursor()
  cursor.execute("SELECT * FROM `USER` WHERE `ID` = %s" , (user_id))

  result = cursor.fetchone()
  connection.close()
  if result is None:
      return None
  
  return User(result)


def connect_db():
    conn = pymysql.connect(
        host="db.steamcenter.tech",
        user="mmiddleton2",
        password=config.password,
        database="mmiddleton2_astrielle",
        autocommit= True,
        cursorclass= pymysql.cursors.DictCursor
    )
    return conn


@app.route("/")
def index():
    return render_template("home.html.jinja")

@app.route("/browse")
def browse():
    connection = connect_db()

    cursor = connection.cursor()

    cursor.execute("SELECT * FROM Product")

    result = cursor.fetchall()

    connection.close()

    return render_template("browse.html.jinja", products=result)

@app.route("/product/<product_id>")
def product_page(product_id):
    connection = connect_db()

    cursor = connection.cursor()

    cursor.execute("SELECT * FROM `Product` WHERE ID = %s", ( product_id ))
    result = cursor.fetchone()

    connection.close()
    
    if result is None:
       abort(404)

    return render_template("product.html.jinja", product=result)
@app.route("/product/<product_id>/add_to_cart", methods=["POST"])
@login_required
def add_to_cart(product_id):
  quantity = request.form["qty"]

  connection = connect_db()
  cursor = connection.cursor()


  cursor.execute("""
    INSERT INTO `Cart` (`Quantity`, `ProductID`, `UserID`)
    VALUES(%s, %s, %s)
    ON DUPLICATE KEY UPDATE
    `Quantity` + %s
 """, (quantity, product_id, current_user.id, quantity))
  
  connection.close()

  return redirect('/cart')

 
@app.route('/sign_up', methods=["POST" , "GET"])
def register():
    if request.method == "POST" :
        name = request.form["name"]

        email = request.form["email"]

        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        address= request.form["address"]

        if password!= confirm_password:
            flash("Passwords do not match")
        elif len(password) < 8:
            flash("Password is too short")
        else:
            return "Thank you for signing up"
        connection = connect_db()

        cursor = connection.cursor()

        try:
          cursor.execute("""
           INSERT INTO `User` (`Name`, `Password`, `Email, `Address`)
           VALUES(%s, %s, %s, %s)
           """, (name ,password, email, address))    
        except pymysql.err.IntegrityError:
          flash("User with that email already exists.")
          connection.close()
        else:
            return redirect('/login')

    return render_template("sign_up.html.jinja")
     
     
     


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        connection = connect_db()

        cursor = connection.cursor()

        cursor.execute("SELECT * FROM `User` WHERE `Email` = %s " , (email) )
        result = cursor.fetchone()

        if result is None:
            flash("No user found.")
        elif password != result["Password"]:
            flash("Incorrect password")
        else:
            login_user(User (result))
            return redirect('/browse')
        print(result)

        connection.close()

    return render_template("login.html.jinja")

@app.route("/logout", methods=["POST", "GET"])
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect("/login")


@app.route('/cart')
@login_required
def cart():
    connection = connect_db

    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM `Cart`
        JOIN `Product` ON `Product`. `ID` = `Cart` . `ProductID`
        WHERE `UserID` = %s  
    """,  (current_user.id))
    results = cursor.fetchall()

    connection.close()


    return render_template("cart.html.jinja", y)