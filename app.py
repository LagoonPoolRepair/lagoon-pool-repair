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
        # Get reCAPTCHA token from form
        recaptcha_response = request.form.get("g-recaptcha-response")
        print("g-recaptcha-response token:", recaptcha_response)
        print("Request headers:", dict(request.headers))

        if not recaptcha_response:
            return jsonify({"success": False, "message": "reCAPTCHA is required."}), 400

        # Verify with Google
        verify_response = requests.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data={
                "secret": RECAPTCHA_SECRET,
                "response": recaptcha_response
            }
        )
        result = verify_response.json()
        print("reCAPTCHA verification result:", result)

        if not result.get("success"):
            return jsonify({
                "success": False,
                "message": f"reCAPTCHA failed: {result.get('error-codes', 'Unknown error')}"
            }), 400

        # Form fields
        first = request.form["firstName"]
        last = request.form["lastName"]
        email = request.form["email"]
        phone = request.form.get("phone", "")
        street = request.form["street"]
        city = request.form["city"]
        state = request.form["state"]
        zip_code = request.form["zip"]
        note = request.form["note"]

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

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
