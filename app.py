from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload   # ⚡ Needed for search
from datetime import datetime


app = Flask(__name__)
app.secret_key = "your_secret_key"

app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:mysql%40123@localhost/lostfound"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ---------------------- MODELS ----------------------
class LostItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100))
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    date_lost = db.Column(db.String(20))
    location_lost = db.Column(db.String(100))
    contact_info = db.Column(db.String(100))

    # ✅ One-to-One to FoundItem
    found_item = db.relationship('FoundItem', backref='lost_item', uselist=False)


class FoundItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100))
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    date_found = db.Column(db.String(20))
    location_found = db.Column(db.String(100))
    contact_info = db.Column(db.String(100))

    # ✅ Foreign Key to LostItem (IMPORTANT!)
    lost_item_id = db.Column(db.Integer, db.ForeignKey('lost_item.id'))


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), default="user")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)




@app.route("/manage_users")
def manage_users():
    users = User.query.all()
    return render_template("manage_users.html", users=users)


@app.route("/delete_user/<int:user_id>")
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for("manage_users"))





@app.route('/')
def home():
    return render_template('index.html')

@app.route('/')
def index():
    return render_template('index.html')

 

@app.route('/report_lost')
def report_lost():
    return render_template('report_lost.html')





@app.route('/admin')
def admin_panel():
    return render_template('admin.html')

@app.route('/admin/lost_reports')
def admin_lost_reports():
    lost_items = LostItem.query.all()
    return render_template('admin_lost_reports.html', lost_items=lost_items)


@app.route('/admin/found_reports')
def admin_found_reports():
    found_items = FoundItem.query.all()
    return render_template('admin_found_reports.html', found_items=found_items)


@app.route('/admin/users')
def admin_users():
    return "Manage users page coming soon"

@app.route('/admin/settings')
def admin_settings():
    return "System settings page coming soon"



@app.route('/verify_report/<int:report_id>', methods=['POST'])
def verify_report(report_id):
    user_answer = request.form['answer'].strip().lower()
    report = LostItem.query.get(report_id)
    
    if report.verification_answer.lower() == user_answer:
        return jsonify({"success": True, "details": report.details})
    else:
        return jsonify({"success": False, "message": "Incorrect answer"})



@app.route('/search', methods=['GET', 'POST'])
def search_items():
    lost_results = []
    found_results = []
    searched = False

    if request.method == 'POST':
        keywords = request.form['keywords'].strip()
        category = request.form['category'].strip()

        # 🔎 Search Lost Items (with relationship to FoundItem)
        lost_results = (
            LostItem.query.options(joinedload(LostItem.found_item))
            .filter(
                LostItem.item_name.ilike(f"%{keywords}%"),
                LostItem.category.ilike(f"%{category}%"),
            )
            .all()
        )

        # 🔎 Search Found Items
        found_results = (
            FoundItem.query
            .filter(
                FoundItem.item_name.ilike(f"%{keywords}%"),
                FoundItem.category.ilike(f"%{category}%"),
            )
            .all()
        )

        searched = True

    return render_template(
        'search.html',
        lost_results=lost_results,
        found_results=found_results,
        searched=searched
    )




# ✅ Endpoint to handle lost.js fetch()
@app.route('/report', methods=['POST'])
def report():
    data = request.get_json()

    new_item = LostItem(
        item_name=data['itemName'],
        description=data['description'],
        category=data['category'],
        date_lost=data['dateLost'],
        location_lost=data['locationLost'],
        contact_info=data['contactInfo']
    )

    db.session.add(new_item)
    db.session.commit()
    return jsonify({"message": "Item reported successfully!"})



    


@app.route('/report_found', methods=['GET', 'POST'])
def report_found():
    if request.method == 'POST':
        try:
            # Collect form data
            item_name = request.form['itemName']
            description = request.form['description']
            category = request.form['category']
            date_found = request.form['dateFound']
            location_found = request.form['locationFound']
            contact_info = request.form['contactInfo']

            # Create SQLAlchemy FoundItem object
            new_item = FoundItem(
                item_name=item_name,
                description=description,
                category=category,
                date_found=date_found,
                location_found=location_found,
                contact_info=contact_info
            )

            # Save to database
            db.session.add(new_item)
            db.session.commit()

            # Flash success message
            flash('✅ Found item reported successfully!', 'success')
            return redirect(url_for('report_found'))

        except Exception as e:
            # Print the exact error for debugging
            print("DEBUG ERROR:", e)
            flash('❌ Something went wrong. Please check console.', 'danger')
            return redirect(url_for('report_found'))

    # GET request
    return render_template('report_found.html')











if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
