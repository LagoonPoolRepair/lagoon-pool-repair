# app.py
from flask import Flask, render_template, request, jsonify
import smtplib
import os
from email.message import EmailMessage
from dotenv import load_dotenv
import requests

load_dotenv()

app = Flask(__name__)

# Email config
EMAIL_ADDRESS = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASS")
TO_EMAIL = os.getenv("TO_EMAIL")
RECAPTCHA_SECRET = os.getenv("RECAPTCHA_SECRET", "6LcLwVgrAAAAAOGg3z6RBh6pZsQhYo1rK2U6EF2U")  # your secret key

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit():
    data = request.form
    recaptcha_response = data.get("g-recaptcha-response")

    # Verify reCAPTCHA
    verify_url = "https://www.google.com/recaptcha/api/siteverify"
    verify_payload = {
        "secret": RECAPTCHA_SECRET,
        "response": recaptcha_response
    }
    recaptcha_result = requests.post(verify_url, data=verify_payload).json()

    if not recaptcha_result.get("success"):
        return jsonify({"success": False, "message": "reCAPTCHA validation failed."}), 400

    try:
        # Extract form fields
        first = data["firstName"]
        last = data["lastName"]
        email = data["email"]
        phone = data.get("phone", "")
        street = data["street"]
        city = data["city"]
        state = data["state"]
        zip_code = data["zip"]
        note = data["note"]

        # Compose email
        msg = EmailMessage()
        msg["Subject"] = "New Pool Service Estimate Request"
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = TO_EMAIL
        msg.set_content(f"""
        New Estimate Request:

        Name: {first} {last}
        Email: {email}
        Phone: {phone}

        Address:
        {street}
        {city}, {state} {zip_code}

        Issue:
        {note}
        """)

        # Send email
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)

        return jsonify({"success": True, "message": "Estimate request submitted successfully."})

    except Exception as e:
        return jsonify({"success": False, "message": f"Error sending request: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
