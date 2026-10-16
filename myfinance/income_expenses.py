from flask import (
    Blueprint, flash, g, redirect, render_template, request, current_app, url_for
)

from .auth import login_required
from .db import get_db, load_cat, load_colors
from markupsafe import Markup
from pyecharts import options as opts
from pyecharts.charts import Pie, Bar, Line
from datetime import datetime
import json

bp = Blueprint('income', __name__)


def handle_income_expenses(income, selected_cat, start_date, end_date):
    db = get_db()

    try:
        data = db.execute('SELECT * FROM data WHERE author_id = ?', (g.user['id'],)).fetchall()
        income_cat, expenses_cat = load_cat()

    except Exception:
        current_app.logger.exception(f"Handle Income Expenses: cannot load data, user: {g.user['id']}")
        flash("Cannot load data")
        return redirect(url_for('dashboard.index'))

    if not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')

    # used for the charts
    pie_chart = None
    line_chart = None
    bar_chart = None

    colors_income, colors_expenses = load_colors()
    colors = colors_income if income else colors_expenses

    total = 0

    # used to sum all the values for each category
    charts_data = {}
    charts_data_by_date = {}

    
    for i in data:
        category = i['category']
        value = i['value']
        date = i['date'].strftime('%Y-%m-%d')

        if bool(i['income']) != income:
            continue

        
        if selected_cat and category != selected_cat and selected_cat != 'all' \
            or start_date and date < start_date \
            or end_date and date > end_date:

            continue

        charts_data[category] = round(charts_data.get(category, 0) + value, 2)
        charts_data_by_date[date] = round(charts_data_by_date.get(date, 0) + value, 2)
        total += value

    total = round(total, 2)

    # sorts
    charts_data = dict(sorted(charts_data.items(), key=lambda x: x[1], reverse=True))   
    charts_data_by_date = dict(sorted(charts_data_by_date.items()))

    # charts
    if charts_data:
        bar_chart = Markup(
            Bar(init_opts=opts.InitOpts(width="100%", height="320px", bg_color="transparent"))
            .add_xaxis(list(charts_data.keys()))
            .set_colors(colors)
            .add_yaxis("", list(charts_data.values()), color_by="data")
            .render_embed()
        )

        line_chart = Markup(
            Line(init_opts=opts.InitOpts(width="100%", height="320px", bg_color="transparent"))
            .add_xaxis(list(charts_data_by_date.keys()))
            .add_yaxis("", list(charts_data_by_date.values()))
            .set_colors(colors)
            .render_embed()
        )
    
        pie_chart = Markup(
            Pie(init_opts=opts.InitOpts(width="100%", height="320px", bg_color="transparent"))
            .add("", list(charts_data.items()), radius=["25%", "70%"], itemstyle_opts=opts.ItemStyleOpts(border_radius=8, border_color="#f4f4f4", border_width=3))
            .set_colors(colors)
            .set_series_opts(label_opts=opts.LabelOpts(is_show=True))
            .set_global_opts(legend_opts=opts.LegendOpts(is_show=False))
            .render_embed()
        )

    return pie_chart, line_chart, bar_chart, data, total, income_cat, expenses_cat, selected_cat, start_date, end_date

@bp.route('/income', methods=('GET',))
@login_required

def income():
    selected_cat = request.args.get('category')
    start_date = request.args.get('start-date')
    end_date = request.args.get('end-date')
    
    pie_chart, line_chart, bar_chart, data, total, income_cat, expenses_cat,  selected_cat, start_date, end_date = handle_income_expenses(True, selected_cat, start_date, end_date)
    
    
    return render_template('dashboard/income.html', pie_chart=pie_chart, line_chart=line_chart, bar_chart=bar_chart, 
                           data=data, income=total, income_cat=income_cat, selected_cat=selected_cat, start_date=start_date, end_date=end_date)


@bp.route('/expenses', methods=('GET',))
@login_required

def expenses():
    selected_cat = request.args.get('category')
    start_date = request.args.get('start-date')
    end_date = request.args.get('end-date')
    
    pie_chart, line_chart, bar_chart, data, total, income_cat, expenses_cat, selected_cat, start_date, end_date = handle_income_expenses(False, selected_cat, start_date, end_date)
    
    
    return render_template('dashboard/expenses.html', pie_chart=pie_chart, line_chart=line_chart, bar_chart=bar_chart, 
                           data=data, expenses=total, expenses_cat=expenses_cat, selected_cat=selected_cat, start_date=start_date, end_date=end_date)
