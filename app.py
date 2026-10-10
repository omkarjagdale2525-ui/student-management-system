import re
import sqlite3

from flask import Flask, flash, redirect, render_template, request, url_for

import database as db

app = Flask(__name__)
app.secret_key = "change-this-in-production"

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate(form):
    """Clean the form input and return (data, list_of_errors)."""
    data = {
        k: form.get(k, "").strip()
        for k in ["roll_no", "name", "email", "phone", "course", "year"]
    }
    data["email"] = data["email"].lower()
    errors = []
    if not data["roll_no"]:
        errors.append("Roll number is required.")
    if len(data["name"]) < 2:
        errors.append("Name must be at least 2 characters.")
    if not EMAIL_RE.match(data["email"]):
        errors.append("Enter a valid email address.")
    if data["phone"] and not (data["phone"].isdigit() and len(data["phone"]) == 10):
        errors.append("Phone must be exactly 10 digits.")
    if not data["course"]:
        errors.append("Course is required.")
    if data["year"] not in {"1", "2", "3", "4"}:
        errors.append("Year must be between 1 and 4.")
    else:
        data["year"] = int(data["year"])
    return data, errors


@app.route("/")
def index():
    search = request.args.get("q", "").strip()
    total, courses = db.get_stats()
    return render_template(
        "index.html",
        students=db.list_students(search),
        search=search,
        total=total,
        courses=courses,
    )


@app.route("/student/<int:student_id>")
def view(student_id):
    student = db.get_student(student_id)
    if student is None:
        flash("Student not found.", "danger")
        return redirect(url_for("index"))
    return render_template("detail.html", student=student)


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        data, errors = validate(request.form)
        if not errors:
            try:
                db.add_student(data)
                flash("Student added successfully.", "success")
                return redirect(url_for("index"))
            except sqlite3.IntegrityError:
                errors.append("Roll number or email already exists.")
        for e in errors:
            flash(e, "danger")
        return render_template("form.html", student=request.form, mode="Add")
    return render_template("form.html", student={}, mode="Add")


@app.route("/edit/<int:student_id>", methods=["GET", "POST"])
def edit(student_id):
    student = db.get_student(student_id)
    if student is None:
        flash("Student not found.", "danger")
        return redirect(url_for("index"))
    if request.method == "POST":
        data, errors = validate(request.form)
        if not errors:
            try:
                db.update_student(student_id, data)
                flash("Student updated successfully.", "success")
                return redirect(url_for("index"))
            except sqlite3.IntegrityError:
                errors.append("Roll number or email already exists.")
        for e in errors:
            flash(e, "danger")
        return render_template("form.html", student=request.form, mode="Edit")
    return render_template("form.html", student=student, mode="Edit")


@app.route("/delete/<int:student_id>", methods=["POST"])
def delete(student_id):
    db.delete_student(student_id)
    flash("Student deleted.", "warning")
    return redirect(url_for("index"))


if __name__ == "__main__":
    db.init_db()
    app.run(debug=True)