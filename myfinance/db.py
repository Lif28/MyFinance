import sqlite3
from datetime import datetime

import click
from flask import current_app, g
import json
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


sqlite3.register_converter(
    "timestamp", lambda v: datetime.fromisoformat(v.decode())
)

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

def load_cat():
    return json.loads(g.user['income_cat']), json.loads(g.user['expenses_cat'])

def load_colors():
    return json.loads(g.user['colors_income']), json.loads(g.user['colors_expenses'])

def load_frequencies():
    return json.loads(g.user['frequencies'])

# Executes rules
def process_rules():
    db = get_db()
    rules = db.execute('SELECT * FROM rules WHERE author_id = ?', (g.user['id'],)).fetchall()

    now = datetime.now()
    today = now.date()

    for rule in rules:
        next_date = rule['next_date']

        while next_date <= today:
            date = f"{next_date} {now.strftime('%H:%M:%S')}"

            db.execute('INSERT INTO data (author_id, date, category, value, income, notes)'
                       ' VALUES (?, ?, ?, ?, ?, ?)',
                       (g.user['id'], date, rule['category'], rule['value'], rule['income'], rule['name']))

            # Calculates next_date
            if rule['frequency'] == 'Daily':
                next_date = next_date + timedelta(days=1)
            elif rule['frequency'] == 'Weekly':
                next_date = next_date + timedelta(days=7)
            elif rule['frequency'] == 'Monthly':
                next_date = next_date + relativedelta(months=1)
            else:
                next_date = next_date + relativedelta(years=1)

        # Updates next_date
        db.execute('UPDATE rules SET next_date = ? WHERE id = ?', (next_date, rule['id']))

    db.commit()
