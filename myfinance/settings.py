from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, send_file, current_app
)
from werkzeug.security import check_password_hash, generate_password_hash

from .db import get_db, load_cat, load_colors
from .auth import login_required
import json, tempfile, os

bp = Blueprint("settings", __name__)


@bp.route("/settings")
@login_required

def settings():
    db = get_db()

    income_cat, expenses_cat = load_cat()
    colors_income, colors_expenses = load_colors()

    user = db.execute("SELECT username, frequencies FROM user WHERE id = ?", (g.user["id"],)).fetchone()

    username = user["username"]
    frequencies = user["frequencies"]


    return render_template("dashboard/settings.html", username=username, frequencies=frequencies, colors_expenses=", ".join(colors_expenses), colors_income=", ".join(colors_income), income_cat=", ".join(income_cat), expenses_cat=", ".join(expenses_cat))


# Password
@bp.route("/settings/change-password", methods=("POST",))
@login_required

def change_password():
    db = get_db()

    old_password = request.form.get("old_password")
    new_password = request.form.get("new_password")
    confirm_password = request.form.get("confirm_password")
    error = None

    if not check_password_hash(g.user["password"], old_password):
        error = "Password Incorrect"
        current_app.logger.warning(f"Change password: wrong old password, user: {g.user['id']}")

    elif new_password != confirm_password:
        error = "The password inserted are different from each other"

    if error is not None:
        flash(error)
        return redirect(url_for("settings.settings"))
        
    
    db.execute("UPDATE user set password = ? WHERE id = ?",
        (generate_password_hash(new_password), g.user["id"]))
    
    db.commit()

    current_app.logger.info(f"Change password: password changed successfully, user: {g.user['id']}")

    session.clear()
    flash("Password changed, login again", "success")
    return redirect(url_for("auth.login"))
    
   

# Categories
@bp.route("/settings/change-categories", methods=("POST",))
@login_required

def change_categories():
    db = get_db()

    # Income and expenses categories
    income_cat = []
    expenses_cat = []

    for c in request.form.get("income_cat", "").split(","):
        c = c.strip()
        if c:
            income_cat.append(c)

    for c in request.form.get("expenses_cat", "").split(","):
        c = c.strip()
        if c:
            expenses_cat.append(c)

    # Errors handling
    error = None

    if not income_cat or not expenses_cat:
        error = "Add at least one category for each type"

    if len(set(income_cat)) != len(income_cat) or len(set(expenses_cat)) != len(expenses_cat):
        error = "Two categories in the same list have the same name"
    
    if set(income_cat) & set(expenses_cat):
        error = "2 or more categories have the same name in Income categories or Expenses categories"

    if not error:    
        db.execute("UPDATE user set income_cat = ?, expenses_cat = ? WHERE id = ?",
            (json.dumps(income_cat), json.dumps(expenses_cat), g.user["id"]))
        
        db.commit()
    else:
        flash(error)

    return redirect(url_for("settings.settings"))


# Colors
@bp.route("/settings/change-colors", methods=("POST",))
@login_required

def change_colors():
    db = get_db()

    # Income and expenses colors
    income_colors = []
    expenses_colors = []

    for c in request.form.get("colors_income", "").split(","):
        c = c.strip()
        if c:
            income_colors.append(c)

    for c in request.form.get("colors_expenses", "").split(","):
        c = c.strip()
        if c:
            expenses_colors.append(c)

    # Errors handling
    error = None

    if not income_colors or not expenses_colors:
        error = "Add at least one color for each type"

    if len(set(income_colors)) != len(income_colors) or len(set(expenses_colors)) != len(expenses_colors):
        error = "Two colors in the same list have the same name"
    
    if set(income_colors) & set(expenses_colors):
        error = "2 or more colors have the same name in Income or Expenses colors"

    if not error:    
        db.execute("UPDATE user set colors_income = ?, colors_expenses = ? WHERE id = ?",
            (json.dumps(income_colors), json.dumps(expenses_colors), g.user["id"]))
        
        db.commit()
    else:
        flash(error)

    return redirect(url_for("settings.settings"))


# Import
@bp.route("/settings/import", methods=("GET", "POST"))
@login_required

def _import():
    if request.method == "GET":
        return render_template("dashboard/import.html")    

    # Post request, file uploaded
    else:
        db = get_db()
    
        file = request.files["file"]

        # Loads file
        try:
            entries = json.load(file)
        except ValueError:
            current_app.logger.exception(f"Import: invalid JSON, user: {g.user['id']}")
            flash("File format non compatible")
            return redirect(url_for("settings.settings"))


        new_income_cat = []
        new_expenses_cat = []

        # Inserts entries in the db
        try:
            for entry in entries:
                if entries[entry][2] == True:
                    new_income_cat.append(entries[entry][0])
                else:
                    new_expenses_cat.append(entries[entry][0])

                db.execute("INSERT INTO data (author_id, date, category, value, income, notes)"
                        " VALUES (?, ?, ?, ?, ?, ?)", (g.user["id"], entry, entries[entry][0], entries[entry][1], entries[entry][2], entries[entry][3]))
                
        except Exception:
            db.rollback()
            current_app.logger.exception(f"Import: cannot import entries, user: {g.user['id']}")
            flash("Cannot import entries")
            return redirect(url_for("settings.settings"))

        # Updates categories
        try:    
            
            income_cat, expenses_cat = load_cat()

            # Removes duplicates
            for c in new_income_cat:
                if c not in income_cat:
                    income_cat.append(c)

            for c in new_expenses_cat:
                if c not in expenses_cat:
                    expenses_cat.append(c)

            db.execute("UPDATE user set income_cat = ?, expenses_cat = ? WHERE id = ?",
                        (json.dumps(income_cat), json.dumps(expenses_cat), g.user["id"]))

            db.commit()

        except Exception:
            db.rollback()
            current_app.logger.exception(f"Import: cannot add categories, user: {g.user['id']}")
            flash("Cannot add categories")
            return redirect(url_for("settings.settings"))


        flash("File imported successfully", "success")
        current_app.logger.info(f"Import: file imported successfully, user: {g.user['id']}")

        return redirect(url_for("settings.settings"))

@bp.route("/settings/export")
@login_required

def export():
    db = get_db()

    data = db.execute("SELECT * FROM data WHERE author_id = ?", (g.user["id"],)).fetchall()

    data_d = {}

    for entry in data:
        data_d[str(entry["date"])] = [entry["category"], entry["value"], entry["income"], entry["notes"]]


    # Tempfile with all entries
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
    tmp.write(json.dumps(data_d, indent=2))
    tmp.close()

    response = send_file(tmp.name, as_attachment=True, download_name="export.json")
    os.remove(tmp.name)

    current_app.logger.info(f"Export: file exported, user: {g.user['id']}")

    return response


@bp.route("/settings/delete", methods=("GET", "POST"))
@login_required

def delete():
    if request.method == "GET":
        return render_template("dashboard/delete.html")

    else:
        db = get_db()
        password = request.form.get('password')

        if not check_password_hash(g.user["password"], password):
            flash("Wrong password")
            current_app.logger.warning(f"Delete: wrong password inserted: {g.user['id']}")
            return redirect(url_for("settings.settings"))

        try:
            db.execute('DELETE FROM data WHERE author_id = ?', (g.user['id'],))
            db.execute('DELETE FROM rules WHERE author_id = ?', (g.user['id'],))
            db.execute('DELETE FROM user WHERE id = ?', (g.user['id'],))
            db.commit()

        except Exception:
            db.rollback()
            current_app.logger.exception(f"Delete: cannot delete account, user: {g.user['id']}")
            flash("Account deleted failed")
            return redirect(url_for("settings.settings"))

        current_app.logger.info(f"Delete: account deleted correctly, user: {g.user['id']}")

        session.clear()
        flash("Account deleted successfully", "success")
        return redirect(url_for("auth.register"))