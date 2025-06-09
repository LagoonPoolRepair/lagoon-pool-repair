from flask import Flask, render_template, request, redirect, flash, jsonify
import smtplib
import os
from email.message import EmailMessage
from dotenv import load_dotenv
import requests

load_dotenv()

app = Flask(__name__, static_folder='static')
app.secret_key = 'your-secret-key'

EMAIL_ADDRESS = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASS")
TO_EMAIL = os.getenv("TO_EMAIL")
RECAPTCHA_SECRET = os.getenv("RECAPTCHA_SECRET")

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit():
    try:
        recaptcha_response = request.form.get("g-recaptcha-response")
        print("Received reCAPTCHA token:", recaptcha_response)

        if not recaptcha_response:
            print("No reCAPTCHA response received.")
            return jsonify({"success": False, "message": "reCAPTCHA is required."}), 400

        verify_response = requests.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data={
                "secret": RECAPTCHA_SECRET,
                "response": recaptcha_response
            }
        )

        print("Google reCAPTCHA verify response:", verify_response.json())

        if not verify_response.json().get("success"):
            return jsonify({"success": False, "message": f"reCAPTCHA failed: {verify_response.json().get('error-codes', [])}"}), 400

        first = request.form["firstName"]
        last = request.form["lastName"]
        email = request.form["email"]
        phone = request.form.get("phone", "")
        street = request.form["street"]
        city = request.form["city"]
        state = request.form["state"]
        zip_code = request.form["zip"]
        note = request.form["note"]

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

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)

        return jsonify({"success": True})
    except Exception as e:
        print("Error during form submission:", e)
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
