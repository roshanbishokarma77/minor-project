import bcrypt
from db import get_connection


# ================= PASSWORD HELPERS =================
def hash_password(plain_password: str) -> str:
    """
    Hashes a plain-text password using bcrypt.
    Returns a string safe to store in the database.
    """
    hashed_bytes = bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt())
    return hashed_bytes.decode("utf-8")  # store as text in SQLite


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Checks a plain-text password (typed at login) against
    the stored bcrypt hash. Returns True if they match.
    """
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except (ValueError, AttributeError):
        # hashed_password wasn't a valid bcrypt hash (e.g. old plaintext row)
        return False


# ================= USER REGISTER =================
def register_user(username, email, password):

    conn = get_connection()
    cursor = conn.cursor()

    try:
        hashed_pw = hash_password(password)

        cursor.execute("""
            INSERT INTO USER
            (username, email, password)
            VALUES (?, ?, ?)
        """, (username, email, hashed_pw))

        conn.commit()
        return True

    except Exception as e:
        print("User Registration Error:", e)
        return False

    finally:
        conn.close()


# ================= USER LOGIN =================
def login_user(username, password):

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT *
            FROM USER
            WHERE username=?
        """, (username,))

        row = cursor.fetchone()

        if row is None:
            return None

        stored_hash = row["password"] if isinstance(row, dict) else row[3]
        # NOTE: index 3 assumes column order (user_ID, username, email, password).
        # If get_connection() returns rows as sqlite3.Row, row["password"] also works.

        if verify_password(password, stored_hash):
            return row
        return None

    except Exception as e:
        print("User Login Error:", e)
        return None

    finally:
        conn.close()


# ================= ADMIN REGISTER =================
def register_admin(username, email, password):

    conn = get_connection()
    cursor = conn.cursor()

    try:
        hashed_pw = hash_password(password)

        cursor.execute("""
            INSERT INTO ADMIN
            (username, email, password)
            VALUES (?, ?, ?)
        """, (username, email, hashed_pw))

        conn.commit()
        return True

    except Exception as e:
        print("Admin Registration Error:", e)
        return False

    finally:
        conn.close()


# ================= ADMIN LOGIN =================
def login_admin(username, password):

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT *
            FROM ADMIN
            WHERE username=?
        """, (username,))

        row = cursor.fetchone()

        if row is None:
            return None

        stored_hash = row["password"] if isinstance(row, dict) else row[3]

        if verify_password(password, stored_hash):
            return row
        return None

    except Exception as e:
        print("Admin Login Error:", e)
        return None

    finally:
        conn.close()


def get_guest_session():
    """
    Returns a default guest user object/dictionary.
    This bypasses database authentication and gives temporary session access.
    """
    return {
        "id": None,
        "username": "Guest",
        "role": "guest",
        "is_authenticated": False
    }