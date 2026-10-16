from flask import (
    Blueprint, flash, g, redirect, render_template, request, current_app, url_for
)

from .auth import login_required
from .db import get_db, load_cat, load_frequencies

bp = Blueprint("rules", __name__)

# index
@bp.route("/rules")
@login_required
def rules():
    db = get_db()

    try:
        rules = db.execute("SELECT * FROM rules WHERE author_id = ?", (g.user["id"],)).fetchall()

    except Exception:
        current_app.logger.exception(f"Rules: cannot load rules, user: {g.user['id']}")
        flash("Cannot load rules")
        return redirect(url_for('dashboard.index'))


    income_cat, expenses_cat = load_cat()
    frequencies = load_frequencies()

    return render_template(
        "dashboard/rules.html", 
        rules=rules, 
        income_cat=income_cat, 
        expenses_cat=expenses_cat,
        frequencies=frequencies
    )


# page to add a rule
@bp.route("/rules/add-rule")
@login_required
def add_rule():

    income_cat, expenses_cat = load_cat()
    frequencies = load_frequencies()

    return render_template(
        "dashboard/add-rule.html", 
        income_cat=income_cat, 
        expenses_cat=expenses_cat, 
        frequencies=frequencies
    )


# Update or insert a rule
@bp.route("/rules/upsert-rule", methods=["POST"])
@login_required
def update():
    db = get_db()

    income_cat, expenses_cat = load_cat()

    name = request.form.get("name")
    category = request.form.get("category")
    income = True if category in income_cat else False
    next_date = request.form.get("date")
    value = request.form.get("value")
    frequency = request.form.get("frequency")
    notes = request.form.get("notes")
    upsert = request.form.get("upsert")
    rule_id = request.form.get("id")
    error = None
    message = None

    # Add rule
    try:
        if upsert == "add":
            db.execute("""INSERT INTO rules (author_id, name, category, value,
                        income, notes, frequency, next_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", (
                        g.user["id"], name, category, value,
                        income, notes, frequency, next_date
                    ))
            message = "Rule added successfully"

        # Update rule
        else:
            if not rule_id:
                error = "Rule id missing"
                flash(error)

            else:
                db.execute("""UPDATE rules SET name = ?, category = ?, value = ?, 
                            income = ?, notes = ?, frequency = ?, next_date = ? WHERE id = ? AND author_id = ?""", 
                            (name, category, value, income, notes, frequency, next_date, rule_id, g.user["id"]))
                message = "Rule updated successfully"
    
    except Exception:
        current_app.logger.exception(f"Upsert Rule: error upserting rule/s, user: {g.user['id']}")
        flash("Cannot add rules")
        return redirect(url_for('rules.rules'))
    
    if message:
        flash(message, "success")   
         
    db.commit()
    return redirect(url_for("rules.rules"))


# Edit rule (single)
@bp.route("/rules/edit-rule", methods=["POST"])
@login_required
def edit():
    db = get_db()

    frequencies = load_frequencies()   
    income_cat, expenses_cat = load_cat()
    rule_id = request.form.get("id")

    if not rule_id:
        error = "Rule id missing"
        flash(error)
        return redirect(url_for("rules.rules"))


    try:
        rule = db.execute("SELECT * FROM rules WHERE id = ? AND author_id = ?", (rule_id, g.user["id"])).fetchone()

    except Exception:
        current_app.logger.exception(f"Edit rules: cannot edit rules, user: {g.user['id']}")
        flash("Cannot edit rules")
        return redirect(url_for('rules.rules'))

    flash("Rules edited successfully", "success")
    current_app.logger.info(f"Edit rules: rules edited, user: {g.user['id']}")
    return render_template("/dashboard/edit-rule.html",
                            rule=rule, 
                            income_cat=income_cat, 
                            expenses_cat=expenses_cat, 
                            frequencies=frequencies
                        )


# Delete rules
@bp.route("/rules/delete", methods=["POST"])
@login_required
def delete():
    db = get_db()

    rule_ids = request.form.getlist("id")

    if not rule_ids:
        error = "Rule id missing"
        flash(error)
        return redirect(url_for("rules.rules"))

    try:
        for rule_id in rule_ids:
            db.execute("DELETE FROM rules WHERE id = ? AND author_id = ?", (rule_id, g.user["id"],))
        db.commit()

    except Exception:
        db.rollback()
        current_app.logger.exception(f"Delete rules: cannot delete rules, user: {g.user['id']}")
        flash("Cannot delete rules")
        return redirect(url_for('rules.rules'))

    flash("Rules deleted successfully", "success")
    current_app.logger.info(f"Delete rules: rules deleted, user: {g.user['id']}")
    return redirect(url_for("rules.rules"))