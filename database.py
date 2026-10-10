import sqlite3

DB_PATH = "students.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                roll_no TEXT NOT NULL UNIQUE,
                name    TEXT NOT NULL,
                email   TEXT NOT NULL UNIQUE,
                phone   TEXT,
                course  TEXT NOT NULL,
                year    INTEGER NOT NULL CHECK (year BETWEEN 1 AND 4)
            )
        """)


def add_student(data):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO students (roll_no, name, email, phone, course, year) "
            "VALUES (:roll_no, :name, :email, :phone, :course, :year)",
            data,
        )


def get_student(student_id):
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM students WHERE id = ?", (student_id,)
        ).fetchone()


def list_students(search=""):
    with get_conn() as conn:
        if search:
            like = f"%{search}%"
            return conn.execute(
                "SELECT * FROM students WHERE name LIKE ? OR roll_no LIKE ? "
                "OR course LIKE ? OR email LIKE ? ORDER BY name",
                (like, like, like, like),
            ).fetchall()
        return conn.execute("SELECT * FROM students ORDER BY name").fetchall()


def update_student(student_id, data):
    data = {**data, "id": student_id}
    with get_conn() as conn:
        conn.execute(
            "UPDATE students SET roll_no=:roll_no, name=:name, email=:email, "
            "phone=:phone, course=:course, year=:year WHERE id=:id",
            data,
        )


def delete_student(student_id):
    with get_conn() as conn:
        conn.execute("DELETE FROM students WHERE id = ?", (student_id,))


def get_stats():
    """Return (total_students, courses) where courses = [(course, count), ...]."""
    with get_conn() as conn:
        total = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
        courses = conn.execute(
            "SELECT course, COUNT(*) AS n FROM students "
            "GROUP BY course ORDER BY n DESC"
        ).fetchall()
        return total, courses