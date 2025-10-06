from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import datetime
import joblib
import os

# ---------------- FLASK SETUP ----------------
app = Flask(__name__)
app.secret_key = "your_secret_key"

# ---------------- DATABASE CONFIG ----------------
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:mysql%40123@localhost/lostfound"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ---------------- LOAD URGENCY MODEL ----------------
MODEL_PATH = os.path.join(os.path.dirname(__file__), "urgency_model.pkl")
if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
else:
    model = None

# ---------------- MODELS ----------------
class Item(db.Model):
    __tablename__ = "items"
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    contact_info = db.Column(db.String(100), nullable=False)
    location_lost = db.Column(db.String(100), nullable=True)
    location_found = db.Column(db.String(100), nullable=True)
    date_lost = db.Column(db.DateTime, nullable=True)
    date_found = db.Column(db.DateTime, nullable=True)
    report_type = db.Column(db.String(10), nullable=True)  # 'lost' or 'found'
    urgency = db.Column(db.String(20), nullable=True)      # 'High', 'Medium', 'Low'

# ---------------- URGENCY PREDICTION FUNCTION ----------------
def predict_urgency(text):
    # Load the trained model and vectorizer
    import joblib
    model = joblib.load("urgency_model.pkl")
    vectorizer = joblib.load("vectorizer.pkl")

    # Transform the text to the same format used in training
    X = vectorizer.transform([text])  # keeps 2D structure

    # Predict the urgency level
    return model.predict(X)[0]



# ----------- REPORT LOST -----------
@app.route("/report_lost", methods=["GET", "POST"])
def report_lost():
    if request.method == "POST":
        item_name = request.form["itemName"]
        description = request.form["description"]
        category = request.form["category"]
        contact_info = request.form["contactInfo"]
        location_lost = request.form["locationLost"]
        date_lost = request.form.get("dateLost")

        # convert date string to datetime
        date_lost_dt = datetime.strptime(date_lost, '%Y-%m-%d') if date_lost else datetime.now()

        new_item = Item(
            item_name=item_name,
            description=description,
            category=category,
            contact_info=contact_info,
            location_lost=location_lost,
            date_lost=date_lost_dt
        )
        db.session.add(new_item)
        db.session.commit()

        flash("Lost item reported successfully!", "success")
        return redirect(url_for("home"))

    return render_template("report_lost.html")


# ----------- REPORT FOUND -----------
@app.route("/report_found", methods=["GET", "POST"])
def report_found():
    if request.method == "POST":
        item_name = request.form["item_name"]
        description = request.form["description"]
        category = request.form["category"]
        contact_info = request.form["contact_info"]
        location_found = request.form["location_found"]
        date_found = request.form["date_found"]

        new_item = Item(
            item_name=item_name,
            description=description,
            category=category,
            contact_info=contact_info,
            location_found=location_found,
            date_found=datetime.strptime(date_found, "%Y-%m-%d")
        )
        db.session.add(new_item)
        db.session.commit()

        flash("Found item reported successfully!", "success")
        return redirect(url_for("home"))

    return render_template("report_found.html")


# ----------- SEARCH ITEMS (Only Found Reports) -----------




# List of stop words to ignore in description
STOP_WORDS = ['of', 'and', 'the', 'a', 'an', 'in', 'on', 'for', 'with']


# ---------------- ADMIN PANEL ----------------
@app.route('/admin')
def admin_panel():
    return render_template('admin.html')

@app.route('/admin/lost_reports')
def admin_lost_reports():
    lost_items = Item.query.filter(Item.date_lost != None).all()
    return render_template('admin_lost_reports.html', lost_items=lost_items)

@app.route('/admin/found_reports')
def admin_found_reports(): 
   found_items = Item.query.filter(Item.date_found != None).all()
   return render_template('admin_found_reports.html', found_items=found_items)
    
    
    
    
@app.route('/search', methods=['GET', 'POST'])
def search_items():
    results = []
    searched = False
    matched_keywords = []  # for template highlighting

    if request.method == 'POST':
        item_name_input = request.form.get('item_name', '').strip().lower()
        description_input = request.form.get('description', '').strip().lower()
        category_input = request.form.get('category', '').strip().lower()

        searched = True

        # Initial query: only found items
        query = Item.query.filter(Item.date_found != None)

        # Match item name (case-insensitive)
        if item_name_input:
            query = query.filter(func.lower(Item.item_name).like(f"%{item_name_input}%"))

        # Match category (case-insensitive)
        if category_input:
            query = query.filter(func.lower(Item.category) == category_input)

        # Execute initial query to get candidates
        candidates = query.all()

        # Match description keywords manually in Python
        if description_input:
            keywords = [w for w in description_input.split() if w not in STOP_WORDS]
            matched_keywords = keywords
            results = []
            for item in candidates:
                item_desc_lower = item.description.lower()
                # Check if any keyword is in the description
                if any(kw in item_desc_lower for kw in keywords):
                    results.append(item)
        else:
            results = candidates

    return render_template('search.html', results=results, searched=searched, keywords=matched_keywords)






# ---------------- HOME PAGE ----------------
@app.route('/')
def home():
    return render_template('index.html')



# ---------------- MAIN ----------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
    app.run(debug=True)



