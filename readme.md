Event Booking System
📌 Project Overview

The Event Booking System is a web-based application developed using Python Flask and MongoDB. It allows users to browse upcoming events, search and filter events by category, and book tickets online. The system also includes an admin panel for managing events efficiently.

This project is suitable for real-world use cases such as concerts, seminars, workshops, and conferences.

🚀 Features
User Features

View all upcoming events

Search events by title

Filter events by category

View event details (date, time, location, price)

Book tickets online

Automatic calculation of total amount

Real-time seat availability update

Admin Features

Secure admin login

Add new events

Update existing events

Delete events

Manage available seats

View all events from dashboard

🛠️ Technologies Used

Backend: Python, Flask

Frontend: HTML, CSS

Database: MongoDB (Atlas)

Other Tools: PyMongo, Flask-CORS, Gunicorn

Deployment: Render

📂 Project Structure
EventBooking/
│
├── app.py
├── requirements.txt
├── templates/
│   ├── index.html
│   ├── all_events.html
│   ├── book.html
│   ├── admin.html
│   └── ...
│
├── static/
│   ├── css/
│   └── images/

⚙️ Installation & Setup (Local)

Clone the repository

git clone https://github.com/your-username/event-booking-system.git


Install dependencies

pip install -r requirements.txt


Set environment variable

MONGO_URI=your_mongodb_connection_string


Run the application

python app.py

🌐 Deployment

The project is deployed on Render using Gunicorn with MongoDB Atlas as the online database.

## Admin Access
Admin credentials are configured for demonstration purposes only.
For security reasons, credentials are not shared publicly.


(Change credentials for production use)

📄 License

This project is created for educational purposes and can be modified or extended as needed.