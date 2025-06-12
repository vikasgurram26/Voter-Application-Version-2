import os
import base64
import json
from google.cloud import vision
import mysql.connector
from flask import *
from functools import wraps
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Limit the maximum content length to 32 MB
app.config['MAX_CONTENT_LENGTH'] = 64 * 1024 * 1024  # 64 MB

# Database configuration (using TCP/IP)

db_config = {
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASS", "6304G.Vik@s"),
    "database": os.getenv("DB_NAME", "Voter-Database"),
    "unix_socket": f"/cloudsql/{os.getenv('INSTANCE_CONNECTION_NAME')}"
}

# ✅ Test MySQL Connection
try:
    conn = mysql.connector.connect(**db_config)
    conn.close()
    print("✅ Database connection successful!")
except mysql.connector.Error as err:
    print(f"❌ Database connection failed: {err}")

# Verify the GOOGLE_APPLICATION_CREDENTIALS environment variable
if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
    print("❌ GOOGLE_APPLICATION_CREDENTIALS environment variable is not set.")
else:
    print(f"✅ GOOGLE_APPLICATION_CREDENTIALS is set to: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS')}")

# Print GOOGLE_APPLICATION_CREDENTIALS environment variable
print(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))

# Add this line to verify the variable within the running app
print(f"GOOGLE_APPLICATION_CREDENTIALS inside app: {os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')}")

# ✅ Ensure JSON Files Exist
for file in ["users.json", "profile.json"]:
    if not os.path.exists(file):
        with open(file, "w") as f:
            json.dump([], f, indent=4)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
def home():
    return send_file('src/index.html')

@app.route("/login")
def login():
    return send_file('src/login.html')

@app.route("/signup")
def signup():
    return send_file('src/signup.html')

@app.route("/vportal", methods=["GET", "POST"])
@login_required
def vportal():
    voter = None
    if request.method == "POST":
        aadhar = request.form["aadhar"]
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM voters WHERE aadhar = %s", (aadhar,))
            voter = cursor.fetchone()
            cursor.close()
            conn.close()

            if voter:
                # Encode binary data to Base64
                voter["fingerprint"] = base64.b64encode(voter["fingerprint"]).decode("utf-8") if voter["fingerprint"] else None
                voter["face"] = base64.b64encode(voter["face"]).decode("utf-8") if voter["face"] else None
            else:
                flash("❌ No voter found with this Aadhar number.", "danger")

        except mysql.connector.Error as err:
            flash(f"❌ Database error: {err}", "danger")

    return render_template("vportal.html", voter=voter)

@app.route("/qrportal")
@login_required
def qrportal():
    return send_file('src/qrportal.html')

@app.route("/faportal")
@login_required
def faportal():
    return send_file('src/faportal.html')

@app.route("/registration")
@login_required
def registration():
    return send_file('src/registration.html')

@app.route("/profile")
def profile():
    return send_file('src/profile.html')

@app.route("/submit", methods=["POST"])
def submit():
    username = request.form["username"]
    password = request.form["password"]

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    try:
        # Check if the username and password match
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()

        if user:
            session['logged_in'] = True
            session['username'] = username  # Store the username in the session
            return redirect(url_for("home"))
        else:
            return '❌ Invalid credentials'

    except mysql.connector.Error as err:
        return f"❌ Database error: {err}"

    finally:
        cursor.close()
        conn.close()

@app.route("/signup-submit", methods=["POST"])
def signup_submit():
    username = request.form["username"]
    email = request.form["email"]
    password = request.form["password"]

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    try:
        # Check if the username or email already exists
        cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
        existing_user = cursor.fetchone()

        if existing_user:
            return render_template("signup.html", errorMessage='❌ Username or email already exists')

        # Insert the new user into the database
        cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, password))
        conn.commit()

    except mysql.connector.Error as err:
        return render_template("signup.html", errorMessage=f"❌ Database error: {err}")

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for("login"))

@app.route("/profile-submit", methods=["POST"])
def profile_submit():
    name = request.form["name"]
    mobile = request.form["mobile"]
    photo = request.files["photo"]

    # Save profile photo
    photo_filename = os.path.join("src/uploads", photo.filename)
    photo.save(photo_filename)

    # Save profile data
    profile_data = {"name": name, "mobile": mobile, "photo": photo_filename}
    with open("profile.json", "w") as f:
        json.dump(profile_data, f, indent=4)

    return redirect(url_for("profile"))

@app.route("/register", methods=["POST"])
def register():
    print("Form Data:", request.form)
    print("Files:", request.files)
    name = request.form["name"]
    phone = request.form["phone"]
    aadhar = request.form["aadhar"]
    house_no = request.form["house_no"]
    street = request.form["street"]
    landmark = request.form["landmark"]
    district = request.form["district"]
    state = request.form["state"]
    postal_pin = request.form["postal_pin"]

    # Fingerprint: always from file upload (based on your current logic)
    fingerprint = request.files["fingerprint_upload"].read()

    # For face image, check if a captured image was provided
    if 'face_capture' in request.form and request.form["face_capture"]:
        # The captured image is stored as a Base64 string (e.g., "data:image/png;base64,...")
        data = request.form["face_capture"]
        # Remove the header (if present)
        match = re.search(r"^data:image/\w+;base64,", data)

        if match:
            data = data[match.end():]
        face = base64.b64decode(data)
    else:
        # Otherwise expect a file upload:
        face = request.files["face_upload"].read()

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO voters (name, phone, aadhar, house_no, street, landmark, district, state, postal_pin, fingerprint, face)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (name, phone, aadhar, house_no, street, landmark, district, state, postal_pin, fingerprint, face))
        conn.commit()
    except mysql.connector.Error as err:
        # handle error.
        print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for("registration"))

@app.route('/scan-fingerprint', methods=['POST'])
def scan_fingerprint():
    # Use the fingerprint scanner SDK to capture the fingerprint
    # This is a placeholder for the actual fingerprint scanning logic
    fingerprint_data = capture_fingerprint()

    # Verify the fingerprint with the database
    is_verified = verify_fingerprint(fingerprint_data)

    if is_verified:
        return jsonify(success=True, message='Fingerprint verified successfully')
    else:
        return jsonify(success=False, message='Fingerprint verification failed')

def capture_fingerprint():
    # Placeholder function to capture fingerprint using the scanner SDK
    # Replace this with actual SDK integration code
    return 'sampleFingerprintData'

def verify_fingerprint(fingerprint_data):
    # Placeholder function to verify fingerprint with the database
    # Replace this with actual verification logic
    return True

@app.route('/validate-face', methods=['POST'])
def validate_face():
    aadhaar_number = request.form.get('aadhaar')
    live_image_base64 = request.form.get('live_image')

    if not aadhaar_number or not live_image_base64:
        return jsonify(success=False, message="Aadhaar number and live image are required"), 400

    # Decode the Base64 live image
    live_image_data = base64.b64decode(live_image_base64.split(',')[1])

    # Connect to the database
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    try:
        # Fetch the stored face image from the database
        cursor.execute("SELECT face FROM voters WHERE aadhar = %s", (aadhaar_number,))
        result = cursor.fetchone()

        if not result or not result['face']:
            return jsonify(success=False, message="No face data found for the given Aadhaar number"), 404

        # Decode the stored face image
        stored_face = result['face']

        # Save the live image to the database
        cursor.execute("UPDATE voters SET live_image = %s WHERE aadhar = %s", (live_image_data, aadhaar_number))
        conn.commit()

        # Add checks for the service account key file
        credentials_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        if credentials_path:
            if os.path.exists(credentials_path):
                if os.access(credentials_path, os.R_OK):
                    print(f"✅ Service account key file found and is readable: {credentials_path}")
                else:
                    print(f"❌ Service account key file found but is NOT readable: {credentials_path}")
            else:
                print(f"❌ Service account key file not found at: {credentials_path}")

        # Use Google Cloud Vision API to compare the images

        # Prepare the stored and live images for comparison
        stored_image = vision.Image(content=stored_face)
        live_image = vision.Image(content=live_image_data)

        # Perform face detection on both images
        stored_response = client.face_detection(image=stored_image)
        live_response = client.face_detection(image=live_image)

        stored_faces = stored_response.face_annotations
        live_faces = live_response.face_annotations

        if not stored_faces or not live_faces:
            return jsonify(success=False, message="Face not detected in one or both images"), 400

        # Simplified comparison logic: Check if faces are detected in both images
        if len(stored_faces) > 0 and len(live_faces) > 0:
            return jsonify(success=True, message="Face verified successfully")
        else:
            return jsonify(success=False, message="Face verification failed")

    except Exception as e:
        return jsonify(success=False, message=f"Error: {str(e)}"), 500

    finally:
        cursor.close()
        conn.close()

@app.route('/check-login-status')
def check_login_status():
    is_logged_in = 'logged_in' in session
    username = session.get('username') if is_logged_in else None
    return jsonify(isLoggedIn=is_logged_in, username=username)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('home'))

def main():
    app.run(port=int(os.environ.get('PORT', 5000)),debug=True)

if __name__ == "__main__":
    main()
