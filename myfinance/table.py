from flask import (
    Blueprint, flash, g, redirect, render_template, request, current_app, url_for
)

from .auth import login_required
from .db import get_db, load_cat, load_frequencies
from datetime import datetime


bp = Blueprint('table', __name__)


@bp.route('/table')
@login_required
def table():
    db = get_db()

    try:
        data = db.execute('SELECT * FROM data WHERE author_id = ?', (g.user['id'],)).fetchall()
        income_cat, expenses_cat = load_cat()
        frequencies = load_frequencies()
        
        # to sort data from the last date to the first 
        data = sorted(data, key=lambda x: x['date'], reverse=True)

        tot_income = 0
        tot_expenses = 0
        total = 0

        for i in data:
            value = i['value']
            if i['income']:
                tot_income += value
            else:
                tot_expenses += value

        total = tot_income-tot_expenses

    except Exception:
        current_app.logger.exception(f"Table: cannot load data, used: {g.user['id']}")
        flash("Cannot load data")
        return redirect(url_for('dashboard.index'))


    return render_template(
        'dashboard/table.html', 
        data=data, 
        income=tot_income, 
        expenses=tot_expenses,
        total=total,
        income_cat=income_cat,
        expenses_cat=expenses_cat,
        entries=data,
        frequencies=frequencies
    )


def handle_actions(action):
    pass


@bp.route('/table/update-entries', methods=['POST'])
@login_required
def update():
    db = get_db()

    entries_ids = request.form.getlist('entry')
    action = request.form.get('action')
    entries = []

    if action == 'edit':

        try:
            income_cat, expenses_cat = load_cat()
            frequencies = load_frequencies()

            for id in entries_ids:
                entry = db.execute('SELECT id, income, category, date, value, notes FROM data WHERE id = ? AND author_id = ?', 
                        (id, g.user['id'])).fetchone()
                
                if entry:
                    entry = dict(entry)
                    entry['date'] = entry['date'].strftime("%Y-%m-%d")
                    entries.append(entry)

        except Exception:
            current_app.logger.exception(f"Update: cannot load entries for editing, user: {g.user['id']}")
            flash("Cannot load entries")
            return redirect(url_for('table.table'))


        flash("Entries updated successfully", "success")
        current_app.logger.info(f"Update entries: entries updated, user: {g.user['id']}")
        return render_template(
            'dashboard/edit-entries.html',
            entries=entries, 
            income_cat=income_cat, 
            expenses_cat=expenses_cat,
            frequencies=frequencies
        )

    elif action == 'delete':
        try:
            for id in entries_ids:
                db.execute('DELETE FROM data WHERE id = ? AND author_id = ?', (id, g.user['id'],))
            db.commit()
        except Exception:
            db.rollback()
            current_app.logger.exception(f"Update: cannot delete entries, user {g.user['id']}")
            flash("Cannot delete entries")
            return redirect(url_for('table.table'))

        flash("Entries deleted", "success")
        return redirect(url_for('table.table'))


@bp.route('/table/save-entries', methods=['POST'])
@login_required
def save():
    db = get_db()

    entries_ids = request.form.getlist('entry_id')
    categories = request.form.getlist('category')
    dates = request.form.getlist('date')
    values = request.form.getlist('value')
    notes = request.form.getlist('notes')

    entries = zip(entries_ids, categories, dates, values, notes)


    # Save
    try:
        for entry_id, category, date, value, notes in entries:

            entry = db.execute('SELECT date FROM data WHERE id = ? AND author_id = ?',
                            (entry_id, g.user['id'])).fetchone()

            if date != entry['date'].strftime("%Y-%m-%d"):
                date = f"{date} {datetime.now().strftime('%H:%M:%S')}"
            else:
                date = entry['date']

            db.execute('UPDATE data SET category = ?, value = ?, date = ?, notes = ? WHERE id = ? AND author_id = ?',
                    (category, value, date, notes, entry_id, g.user['id']))

        db.commit()

    except Exception:
        db.rollback()
        current_app.logger.exception(f"Save: cannot save entries, user {g.user['id']}")
        flash("Cannot save entries")
        return redirect(url_for('table.table'))

    current_app.logger.info(f"Save: entries updated, user {g.user['id']}")
    flash("Entries saved", "success")
    return redirect(url_for('table.table'))