from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

import sqlite3

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)


# =========================================================
# FLASK SETUP
# =========================================================

app = Flask(__name__)

app.secret_key = "doc_web_demo_secret"

DATABASE = "doctor.db"


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_db():

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    return conn


# =========================================================
# INITIALIZE DATABASE
# =========================================================

def init_db():

    conn = get_db()

    cursor = conn.cursor()


    # =====================================================
    # DOCTOR TABLE
    # =====================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS doctor (

            id INTEGER PRIMARY KEY,

            name TEXT NOT NULL,

            specialization TEXT NOT NULL,

            clinic_name TEXT NOT NULL,

            about TEXT NOT NULL,

            phone TEXT NOT NULL,

            address TEXT NOT NULL,

            timings TEXT NOT NULL

        )
    """)


    # =====================================================
    # USERS TABLE
    # =====================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            username TEXT UNIQUE NOT NULL,

            password TEXT NOT NULL

        )
    """)


    # =====================================================
    # SERVICES TABLE
    # =====================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS services (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            description TEXT NOT NULL

        )
    """)


    # =====================================================
    # DEFAULT DOCTOR
    # =====================================================

    doctor = cursor.execute("""
        SELECT *
        FROM doctor
        WHERE id = 1
    """).fetchone()


    if not doctor:

        cursor.execute("""
            INSERT INTO doctor
            (
                id,
                name,
                specialization,
                clinic_name,
                about,
                phone,
                address,
                timings
            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (

            1,

            "Dr. Hari",

            "Dermatologist",

            "Hari Skin & Aesthetic Clinic",

            "Dr. Hari provides personalized dermatology care with a focus on healthy skin, hair and confidence.",

            "+91 9876543210",

            "Indiranagar, Bengaluru, Karnataka",

            "Monday - Saturday | 9:00 AM - 7:00 PM"

        ))


    # =====================================================
    # DEFAULT DOCTOR LOGIN
    # =====================================================

    user = cursor.execute("""
        SELECT *
        FROM users
        WHERE username = ?
    """, (
        "drhari",
    )).fetchone()


    if not user:

        password_hash = generate_password_hash(
            "admin123"
        )

        cursor.execute("""
            INSERT INTO users
            (
                username,
                password
            )

            VALUES (?, ?)
        """, (

            "drhari",

            password_hash

        ))


    # =====================================================
    # DEFAULT SERVICES
    # =====================================================

    service_count = cursor.execute("""
        SELECT COUNT(*) AS count
        FROM services
    """).fetchone()["count"]


    if service_count == 0:

        services = [

            (
                "✨ Acne & Scar Care",

                "Personalized solutions for acne, pigmentation and acne scars."
            ),

            (
                "🌿 Skin Wellness",

                "Professional consultation for common skin concerns."
            ),

            (
                "💫 Hair & Scalp Care",

                "Care plans for hair fall, dandruff and scalp conditions."
            ),

            (
                "💎 Cosmetic Dermatology",

                "Aesthetic treatments designed around your skin goals."
            )

        ]


        cursor.executemany("""
            INSERT INTO services
            (
                name,
                description
            )

            VALUES (?, ?)
        """, services)


    conn.commit()

    conn.close()


# =========================================================
# PUBLIC WEBSITE
# =========================================================

@app.route("/")
def home():

    conn = get_db()


    doctor = conn.execute("""
        SELECT *
        FROM doctor
        WHERE id = 1
    """).fetchone()


    services = conn.execute("""
        SELECT *
        FROM services
        ORDER BY id
    """).fetchall()


    conn.close()


    return render_template(

        "index.html",

        doctor=doctor,

        services=services

    )


# =========================================================
# DOCTOR LOGIN
# =========================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        username = request.form[
            "username"
        ].strip()

        password = request.form[
            "password"
        ]


        conn = get_db()


        user = conn.execute("""
            SELECT *
            FROM users
            WHERE username = ?
        """, (
            username,
        )).fetchone()


        conn.close()


        if user and check_password_hash(
            user["password"],
            password
        ):

            # Store logged-in username
            # in the session.
            session["logged_in"] = True

            session["username"] = user["username"]


            return redirect(
                url_for("dashboard")
            )


        flash(
            "Incorrect username or password."
        )


    return render_template(
        "login.html"
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()


    return redirect(
        url_for("home")
    )


# =========================================================
# DOCTOR DASHBOARD
# =========================================================

@app.route(
    "/dashboard",
    methods=["GET", "POST"]
)
def dashboard():

    # -----------------------------------------------------
    # CHECK LOGIN
    # -----------------------------------------------------

    if not session.get("logged_in"):

        return redirect(
            url_for("login")
        )


    conn = get_db()


    # -----------------------------------------------------
    # UPDATE DOCTOR INFORMATION
    # -----------------------------------------------------

    if request.method == "POST":

        name = request.form[
            "name"
        ].strip()


        specialization = request.form[
            "specialization"
        ].strip()


        clinic_name = request.form[
            "clinic_name"
        ].strip()


        about = request.form[
            "about"
        ].strip()


        phone = request.form[
            "phone"
        ].strip()


        address = request.form[
            "address"
        ].strip()


        timings = request.form[
            "timings"
        ].strip()


        conn.execute("""
            UPDATE doctor

            SET

                name = ?,

                specialization = ?,

                clinic_name = ?,

                about = ?,

                phone = ?,

                address = ?,

                timings = ?

            WHERE id = 1
        """, (

            name,

            specialization,

            clinic_name,

            about,

            phone,

            address,

            timings

        ))


        conn.commit()


        flash(
            "✨ Website information updated successfully!"
        )


    # -----------------------------------------------------
    # GET DOCTOR
    # -----------------------------------------------------

    doctor = conn.execute("""
        SELECT *
        FROM doctor
        WHERE id = 1
    """).fetchone()


    # -----------------------------------------------------
    # GET SERVICES
    # -----------------------------------------------------

    services = conn.execute("""
        SELECT *
        FROM services
        ORDER BY id
    """).fetchall()


    conn.close()


    return render_template(

        "dashboard.html",

        doctor=doctor,

        services=services

    )


# =========================================================
# ADD SERVICE
# =========================================================

@app.route(
    "/add-service",
    methods=["POST"]
)
def add_service():

    if not session.get("logged_in"):

        return redirect(
            url_for("login")
        )


    name = request.form[
        "service_name"
    ].strip()


    description = request.form[
        "service_description"
    ].strip()


    if not name or not description:

        flash(
            "Please enter both service name and description."
        )

        return redirect(
            url_for("dashboard")
        )


    conn = get_db()


    conn.execute("""
        INSERT INTO services
        (
            name,
            description
        )

        VALUES (?, ?)
    """, (

        name,

        description

    ))


    conn.commit()

    conn.close()


    flash(
        "✨ New service added."
    )


    return redirect(
        url_for("dashboard")
    )


# =========================================================
# DELETE SERVICE
# =========================================================

@app.route(
    "/delete-service/<int:service_id>"
)
def delete_service(service_id):

    if not session.get("logged_in"):

        return redirect(
            url_for("login")
        )


    conn = get_db()


    conn.execute("""
        DELETE FROM services

        WHERE id = ?
    """, (
        service_id,
    ))


    conn.commit()

    conn.close()


    flash(
        "Service removed."
    )


    return redirect(
        url_for("dashboard")
    )


# =========================================================
# CHANGE PASSWORD
# =========================================================

@app.route(
    "/change-password",
    methods=["POST"]
)
def change_password():

    # -----------------------------------------------------
    # CHECK LOGIN
    # -----------------------------------------------------

    if not session.get("logged_in"):

        return redirect(
            url_for("login")
        )


    # -----------------------------------------------------
    # GET FORM DATA
    # -----------------------------------------------------

    current_password = request.form[
        "current_password"
    ]


    new_password = request.form[
        "new_password"
    ]


    confirm_password = request.form[
        "confirm_password"
    ]


    # -----------------------------------------------------
    # CHECK PASSWORD LENGTH
    # -----------------------------------------------------

    if len(new_password) < 8:

        flash(
            "New password must be at least 8 characters long."
        )

        return redirect(
            url_for("dashboard")
        )


    # -----------------------------------------------------
    # CHECK PASSWORD MATCH
    # -----------------------------------------------------

    if new_password != confirm_password:

        flash(
            "New password and confirmation password do not match."
        )

        return redirect(
            url_for("dashboard")
        )


    # -----------------------------------------------------
    # GET CURRENTLY LOGGED-IN USER
    # -----------------------------------------------------

    username = session.get(
        "username"
    )


    if not username:

        session.clear()

        return redirect(
            url_for("login")
        )


    conn = get_db()


    user = conn.execute("""
        SELECT *
        FROM users
        WHERE username = ?
    """, (
        username,
    )).fetchone()


    # -----------------------------------------------------
    # CHECK CURRENT PASSWORD
    # -----------------------------------------------------

    if not user or not check_password_hash(

        user["password"],

        current_password

    ):

        conn.close()


        flash(
            "Current password is incorrect."
        )


        return redirect(
            url_for("dashboard")
        )


    # -----------------------------------------------------
    # HASH NEW PASSWORD
    # -----------------------------------------------------

    new_password_hash = generate_password_hash(
        new_password
    )


    # -----------------------------------------------------
    # UPDATE PASSWORD
    # -----------------------------------------------------

    conn.execute("""
        UPDATE users

        SET password = ?

        WHERE username = ?
    """, (

        new_password_hash,

        username

    ))


    conn.commit()

    conn.close()


    flash(
        "🔐 Password changed successfully!"
    )


    return redirect(
        url_for("dashboard")
    )


# =========================================================
# INITIALIZE DATABASE
# =========================================================

init_db()


# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )