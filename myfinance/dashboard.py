from flask import (
    Blueprint, flash, g, redirect, render_template, request, current_app, url_for
)

from .auth import login_required
from .db import get_db, load_cat, load_colors
from markupsafe import Markup
from pyecharts import options as opts
from pyecharts.charts import Pie
from datetime import datetime


bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@bp.route('/')
@login_required
def index():
    COLORS_INCOME, COLORS_EXPENSES = load_colors()
    income_cat, expenses_cat = load_cat()
    
    db = get_db()

    try:
        data = db.execute('SELECT * FROM data WHERE author_id = ?', (g.user['id'],)).fetchall()
        
    except Exception:
        current_app.logger.exception(f"dashboard: cannot load categories, user: {g.user['id']}")
        flash("Cannot load categories")
        return redirect(url_for('settings.settings'))
        

    # used for the charts
    income_pie = None
    expenses_pie = None

    tot_income = 0
    tot_expenses = 0
    total = 0

    # used to sum all the values for each category
    income_data = {}
    expenses_data = {}

    for i in data:
        category = i['category']
        value = i['value']

        if i['income']:
            income_data[category] = round(income_data.get(category, 0) + value, 2)
            tot_income += value
        else:
            expenses_data[category] = round(expenses_data.get(category, 0) + value, 2)
            tot_expenses += value

    tot_income = round(tot_income, 2)
    tot_expenses = round(tot_expenses, 2)
    total = round(tot_income-tot_expenses, 2)


    # sorts
    income_data = dict(sorted(income_data.items(), key=lambda x: x[1], reverse=True))   
    expenses_data = dict(sorted(expenses_data.items(), key=lambda x: x[1], reverse=True))   
    
    # charts
    if income_data:        
        income_pie = Markup(
            Pie(init_opts=opts.InitOpts(width="100%", height="320px", bg_color="transparent"))
                .add("", list(income_data.items()), radius=["25%", "70%"], itemstyle_opts=opts.ItemStyleOpts(border_radius=8, border_color="#f4f4f4", border_width=3))
                .set_colors(COLORS_INCOME)
                .set_series_opts(label_opts=opts.LabelOpts(is_show=True))
                .set_global_opts(legend_opts=opts.LegendOpts(is_show=False))
                .render_embed()
            )
        
    if expenses_data:
        expenses_pie = Markup(
            Pie(init_opts=opts.InitOpts(width="100%", height="320px", bg_color="transparent"))
            .add("", list(expenses_data.items()), radius=["25%", "70%"], itemstyle_opts=opts.ItemStyleOpts(border_radius=8, border_color="#f4f4f4", border_width=3))
            .set_colors(COLORS_EXPENSES)
            .set_series_opts(label_opts=opts.LabelOpts(is_show=True))
            .set_global_opts(legend_opts=opts.LegendOpts(is_show=False))
            .render_embed()
        )
         
    return render_template('dashboard/index.html', income_chart=income_pie, expenses_chart=expenses_pie,
                           data=data, income=tot_income, expenses=tot_expenses, total=total,
                           income_cat=income_cat, expenses_cat=expenses_cat)



@bp.route("/add-entry", methods=["POST"])
@login_required
def add_entry():
    error = None
    category = request.form["category"]
    amount = request.form["value"]
    notes = request.form["notes"]
    income = request.form["income"] == "true"
    
    # .get because not always there's a fixed date
    date = request.form.get("date")
    
    if not date:
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    else:
        date = f"{date} {datetime.now().strftime('%H:%M:%S')}"


    if not category or not amount:
        error = 'Category or Amount missing or incorrect'


    if error:
        flash(error)
        current_app.logger.error(f"Add Entry: {error}, user: {g.user['id']}")

    else:
        db = get_db()

        try:
            db.execute('INSERT INTO data (author_id, date, category, value, income, notes)'
                    ' VALUES (?, ?, ?, ?, ?, ?)',
                    (g.user['id'], date, category, float(amount), bool(income), notes))
            db.commit()
        except Exception:
            current_app.logger.exception(f"Add Entry: cannot add entry, user: {g.user['id']}")
            flash("Cannot add entry")
            return redirect(url_for('dashboard.index'))
            
        flash("Entry added successfully", "success")
        current_app.logger.info(f"Add Entry: entry added successfully, user: {g.user['id']}")

    return redirect(url_for("dashboard.index"))