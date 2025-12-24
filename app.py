from flask import Flask, render_template, request, redirect, session
from flask_cors import CORS
from dotenv import load_dotenv
from bson import ObjectId
from pymongo import MongoClient
from datetime import datetime
import os

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

# Flask App
app = Flask(__name__)
CORS(app)
app.secret_key = "secret123"

# MongoDB
client = MongoClient(MONGO_URI)
db = client["EventBookingDB"]
events_collection = db["events"]
bookings_collection = db["bookings"]

# Admin password
ADMIN_USER = "admin"
ADMIN_PASS = "12345"

def str_to_date(d):
    try:
        return datetime.strptime(d, "%Y-%m-%d").date()
    except:
        return None


# HOME PAGE 

@app.route("/")
def home():
    all_events = list(events_collection.find().sort("date", 1))

    today = datetime.now().date()
    today_str = today.strftime("%Y-%m-%d")

    # upcoming events
    upcoming = []
    for e in all_events:
        edate = str_to_date(e.get("date", ""))
        if edate and edate >= today:
            upcoming.append(e)
        elif not edate:
            upcoming.append(e)

    # CATEGORY-WISE GROUPING
    categories = {}
    for e in all_events:
        cat = e.get("category", "Other")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(e)

    return render_template("index.html",
                           upcoming=upcoming,
                           all_events=all_events,
                           categories=categories,
                           today=today_str,
                           is_admin=session.get("role") == "admin",
                           title="Home")


# ABOUT PAGE
@app.route("/about")
def about():
    return render_template("about.html",
                           is_admin=session.get("role") == "admin",
                           title="About Us")



# CONTACT PAGE
@app.route("/contact")
def contact():
    return render_template("contact.html",
                           is_admin=session.get("role") == "admin",
                           title="Contact Us")

# ALL EVENTS
@app.route("/all-events")
def all_events():
    search = request.args.get("search")
    category = request.args.get("category")

    query = {}
    if search:
        query["title"] = {"$regex": search, "$options": "i"}
    if category:
        query["category"] = category

    events = list(events_collection.find(query).sort("date", 1))

    today = datetime.now().strftime("%Y-%m-%d")

    return render_template("all_events.html",
                           events=events,
                           today=today,
                           is_admin=session.get("role") == "admin",
                           title="All Events")

# BOOK EVENT PAGE
@app.route("/book/<eid>")
def book_event(eid):
    event = events_collection.find_one({"_id": ObjectId(eid)})
    if not event:
        return "Event not found", 404

    try:
        event["price"] = int(event.get("price", 0))
    except:
        event["price"] = 0

    return render_template("book.html",
                           event=event,
                           is_admin=session.get("role") == "admin",
                           title="Book Event")


# BOOK TICKET (POST)
@app.route("/book-ticket", methods=["POST"])
def book_ticket():
    event_id = request.form.get("event_id")
    name = request.form.get("user_name")
    email = request.form.get("user_email")

    seats = int(request.form.get("seats", 0))

    event = events_collection.find_one({"_id": ObjectId(event_id)})
    if not event:
        return "Event not found", 404

    price = int(event.get("price", 0))
    total_amount = price * seats

    booking_doc = {
        "event_id": event_id,
        "user_name": name,
        "user_email": email,
        "seats": seats,
        "total_amount": total_amount,
        "created_at": datetime.now()
    }
    bookings_collection.insert_one(booking_doc)

    events_collection.update_one(
        {"_id": ObjectId(event_id)},
        {"$inc": {"available_seats": -seats}}
    )

    return render_template("booking_success.html",
                           success=True,
                           message=f"Booking Successful! Total Amount = Rs {total_amount}",
                           booking=booking_doc,
                           is_admin=session.get("role") == "admin",
                           title="Booking Success")

# ADMIN LOGIN
@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if session.get("role") == "admin":
        return redirect("/admin/dashboard")

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == ADMIN_USER and password == ADMIN_PASS:
            session["role"] = "admin"  
            return redirect("/admin/dashboard")

        return render_template("admin_login.html",
                               error="Invalid Credentials",
                               is_admin=False,
                               title="Admin Login")

    return render_template("admin_login.html",
                           is_admin=False,
                           title="Admin Login")


# ADMIN DASHBOARD
@app.route("/admin/dashboard")
def admin_dashboard():
    if session.get("role") != "admin":
        return redirect("/admin")

    events = list(events_collection.find().sort("date", 1))

    return render_template("admin.html",
                           events=events,
                           is_admin=True,
                           title="Admin Panel")



# ADD EVENT
@app.route("/add-event", methods=["GET", "POST"])
def add_event():
    if session.get("role") != "admin":
        return redirect("/admin")

    if request.method == "POST":
        event_date = request.form.get("date")
        today = datetime.now().strftime("%Y-%m-%d")

        if event_date < today:
            return render_template("add_event.html",
                                   error="Event date cannot be in the past!",
                                   is_admin=True,
                                   title="Add Event")

        events_collection.insert_one({
            "title": request.form.get("title"),
            "category": request.form.get("category"),
            "date": event_date,
            "time": request.form.get("time"),
            "location": request.form.get("location"),
            "price": int(request.form.get("price")),
            "available_seats": int(request.form.get("available_seats")),
            "image": request.form.get("image") or ""
        })

        return redirect("/admin/dashboard")

    return render_template("add_event.html",
                           is_admin=True,
                           title="Add Event")


# UPDATE EVENT
@app.route("/update-event/<eid>", methods=["GET", "POST"])
def update_event(eid):
    if session.get("role") != "admin":
        return redirect("/admin")

    event = events_collection.find_one({"_id": ObjectId(eid)})

    if request.method == "POST":
        update_data = {
            "title": request.form.get("title"),
            "category": request.form.get("category"),
            "date": request.form.get("date"),
            "time": request.form.get("time"),
            "location": request.form.get("location"),
            "price": int(request.form.get("price")),
            "available_seats": int(request.form.get("available_seats")),
            "image": request.form.get("image") or ""
        }

        today = datetime.now().strftime("%Y-%m-%d")
        if update_data["date"] < today:
            return render_template("update_event.html",
                                   event=event,
                                   error="Event date cannot be in the past!",
                                   is_admin=True,
                                   title="Update Event")

        events_collection.update_one(
            {"_id": ObjectId(eid)},
            {"$set": update_data}
        )

        return redirect("/admin/dashboard")

    return render_template("update_event.html",
                           event=event,
                           is_admin=True,
                           title="Update Event")


# DELETE EVENT
@app.route("/delete-event/<eid>")
def delete_event(eid):
    if session.get("role") != "admin":
        return redirect("/admin")

    events_collection.delete_one({"_id": ObjectId(eid)})
    return redirect("/admin/dashboard")

# LOGOUT

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/admin")

# START SERVER
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

