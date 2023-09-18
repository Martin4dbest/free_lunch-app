from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime

app = Flask(__name__)
app.secret_key = '29f1622f8e3d54fa483f4eb9c225b4fb'  # Set a secret key for session management

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///free_lunch.db'
db = SQLAlchemy(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# Define the User model for authentication
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# Define the Lunch model
class Lunch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    price = db.Column(db.Float, nullable=False)

# Define the Order model
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lunch_id = db.Column(db.Integer, db.ForeignKey('lunch.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    lunch = db.relationship('Lunch', backref=db.backref('orders', lazy=True))

# Define the Meal model
class Meal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    user = db.relationship('User', backref=db.backref('meals', lazy=True))

# Create the database tables
with app.app_context():
    db.create_all()

# Define the user_loader function
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# User login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:  # Replace with proper password hashing
            login_user(user)
            flash('Login successful', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Login failed. Please check your credentials.', 'danger')
    return render_template('login.html')

# User logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

# Index route
@app.route('/')
def index():
    lunches = Lunch.query.all()
    return render_template('index.html', lunches=lunches)

# Order a lunch route
@app.route('/order/<int:lunch_id>', methods=['POST'])
@login_required
def order(lunch_id):
    lunch = Lunch.query.get_or_404(lunch_id)
    new_order = Order(lunch=lunch)
    db.session.add(new_order)
    db.session.commit()
    flash('Order placed successfully!', 'success')
    return redirect(url_for('index'))

# Order history route
@app.route('/orders')
@login_required
def order_history():
    orders = Order.query.order_by(Order.timestamp.desc()).all()
    return render_template('order_history.html', orders=orders)

# List meals route
@app.route('/meals')
@login_required
def list_meals():
    meals = Meal.query.filter_by(user_id=current_user.id).all()
    return render_template('meals/list.html', meals=meals)

# Create meal route
@app.route('/meals/create', methods=['GET', 'POST'])
@login_required
def create_meal():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        meal = Meal(name=name, description=description, user_id=current_user.id)
        db.session.add(meal)
        db.session.commit()
        flash('Meal created successfully', 'success')
        return redirect(url_for('list_meals'))
    return render_template('meals/create.html')

# Dashboard route to display user's meals
@app.route('/dashboard/meals')
@login_required
def dashboard_meals():
    meals = Meal.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard/meals.html', meals=meals)

# Dashboard route to display user's order history
@app.route('/dashboard/orders')
@login_required
def dashboard_orders():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.timestamp.desc()).all()
    return render_template('dashboard/orders.html', orders=orders)

if __name__ == '__main__':
    app.run(debug=True)
