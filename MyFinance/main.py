# MIT License

# Copyright (c) 2026 lif28

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from nicegui import ui
import json
import os
from pathlib import Path
import datetime

INCOME_CATEGORIES = ["Salary", "Sales", "Investments", "Gifts", "Other"]
EXPENSE_CATEGORIES = ["Sport", "School", "Shopping", "Food", "Health", "Transport", "Bills", "Other"]
TIME_CATEGORIES = ["All time", "Last month", "Last Year"]
home = Path.home() / "MyFinance" / "MyFinance"
path_data = home/"data.json"
icon = home/"icon.ico"
date = None

def get_totals(data, date=None, period=None):
    income = {}
    expenses = {}
    total = {}

    if data:
        for entry in data:
            time = entry["Date"].split(" ")[0][0:7]
            cat = entry["Category"]
            amount = float(entry["Amount"])

            # Checks for filters
            if not date or \
                (period.value == TIME_CATEGORIES[1] and date == time) or \
                (period.value == TIME_CATEGORIES[2] and date[0:4]==time[0:4]):

                total[cat] = total.get(cat, 0) + amount # Adds the amount to the total even if is negative

                if amount < 0:
                    amount *= -1
                    expenses[cat] = expenses.get(cat, 0) + amount
                else:
                    income[cat] = income.get(cat, 0) + amount

    return income, expenses, total

def save(category, amount=None, notes=None, expense=False):
    # Checks
    if not amount.replace(".", "", 1).replace("-", "").isdigit():
        return ui.notify("The amount must be a digit!", type="warning")

    if expense and float(amount) > 0:
        amount = str(float(amount) * -1)

    info = {"Category": category, "Amount": amount, "Notes": notes, "Date": str(datetime.datetime.now()).split(".")[0]}
    if os.path.exists(path_data):
        with open(path_data, "r") as file:
            data = json.load(file)
    else:
        data = []

    # Writes info
    data.append(info)

    with open(path_data, "w") as file:
        json.dump(data, file, indent=4)

    return ui.notify("Entry added!", type="positive"), ui.run_javascript('setTimeout(() => { location.reload(); }, 1000);')

def check_data():
    if os.path.exists(path_data):
        with open(path_data, "r") as file:
            return json.load(file)
    else:
        return None

async def delete():
    entries = await grid.get_selected_rows()

    # Checks
    if not entries:
        return ui.notify("Entry not found!", type="negative")

    if os.path.exists(path_data):
        with open(path_data, "r") as file:
            data = json.load(file)

    # Removes the specific entry
    selected_dates = [entry["Date"] for entry in entries if "Date" in entry]
    data = [entry for entry in data if entry["Date"] not in selected_dates]

    with open(path_data, "w") as file:
        json.dump(data, file, indent=4)

    return ui.notify("Entry removed!", type="positive"), ui.run_javascript('setTimeout(() => { location.reload(); }, 1000);')

async def edit():
    row = await grid.get_selected_row()

    # Checks
    if not row:
        return ui.notify("Entry not found!", type="negative")

    mode = False if float(row["Amount"]) > 0 else True

    if os.path.exists(path_data):
        with open(path_data, "r") as file:
            data = json.load(file)

    def edit_entry(category, amount=None, notes=None, data=data):
        # Deletes old entry
        data = [entry for entry in data if entry["Date"] != row["Date"]]

        with open(path_data, "w") as file:
            json.dump(data, file, indent=4)

        # Adds new entry
        save(category, amount=amount, notes=notes, expense=mode)

    # Edit
    with ui.dialog() as dialog:
        with ui.card().style("align-items: center;"):
            ui.label("Edit entry")

            income_category = ui.select(INCOME_CATEGORIES if not mode else EXPENSE_CATEGORIES, value=row["Category"])
            income_amount = ui.input(label='Amount', value=row["Amount"])

            # Notes input
            with ui.input(placeholder="Notes...", value=row["Notes"]).props('rounded outlined dense') as income_notes:
                ui.button(color='orange-8', on_click=lambda: income_notes.set_value(None), icon='delete') \
                .props('flat dense').bind_visibility_from(income_notes, 'value')


            ui.button('Save', on_click=lambda: edit_entry(income_category.value, income_amount.value, income_notes.value))

    dialog.open()

def set_date(period):
    global date
    if period.value == TIME_CATEGORIES[1]:
        date = str(datetime.datetime.now()).split(" ")[0][0:7]
    elif period.value == TIME_CATEGORIES[2]:
        date = str(datetime.datetime.now()).split(" ")[0][0:4]
    else:
        date = None

    income_totals, expense_totals, total = get_totals(check_data(), date, period)

    # Update charts info
    income_chart.options['title']['text'] = f'Income: {round(sum(income_totals.values()), 2)}'
    income_chart.options['series'][0]['data'] = [{'name': name, 'value': val} for name, val in income_totals.items()]

    total_chart.options['title']['text'] = f'Total: {round(sum(total.values()), 2)}'
    total_chart.options['series'][0]['data'] = [{'value': val, 'itemStyle': {'color': '#91cc75' if val >= 0 else '#ee6666'}} for val in total.values()]
    total_chart.options['xAxis']['data'] = list(total.keys())

    expenses_chart.options['title']['text'] = f'Expenses: {round(sum(expense_totals.values()), 2)}'
    expenses_chart.options['series'][0]['data'] = [{'name': name, 'value': val} for name, val in expense_totals.items()]

    # Updates
    income_chart.update()
    total_chart.update()
    expenses_chart.update()


ui.page_title('MyFinance')
ui.add_head_html('<style>body {background-color: #f5f5f5; }</style>')

# Income / Expense
with ui.row().style("margin: 50px auto 0; gap: 200px; display: flex;"):
    with ui.card():
        ui.label("Income")
        income_category = ui.select(INCOME_CATEGORIES, value=INCOME_CATEGORIES[0])
        income_amount = ui.input(label='Amount', placeholder='...')

        # Notes input
        with ui.input(placeholder='Notes...').props('rounded outlined dense') as income_notes:
            ui.button(color='orange-8', on_click=lambda: income_notes.set_value(None), icon='delete') \
            .props('flat dense').bind_visibility_from(income_notes, 'value')

        ui.button('Save', on_click=lambda: save(income_category.value, income_amount.value, income_notes.value))

    with ui.card():
        ui.label("Expenses")
        expense_category = ui.select(EXPENSE_CATEGORIES, value=EXPENSE_CATEGORIES[-1])
        expense_amount = ui.input(label='Amount', placeholder='...')

        # Notes input
        with ui.input(placeholder='Notes...').props('rounded outlined dense') as expense_notes:
            ui.button(color='orange-8', on_click=lambda: expense_notes.set_value(None), icon='delete') \
            .props('flat dense').bind_visibility_from(expense_notes, 'value')

        ui.button('Save', on_click=lambda: save(expense_category.value, expense_amount.value, expense_notes.value, True))

# Dropdown Button
with ui.row().style("margin: 50px auto 0; gap: 200px; display: flex;"):
    period = ui.select(TIME_CATEGORIES, value=TIME_CATEGORIES[0], on_change=set_date)

# Charts
with ui.row().style("margin: 50px auto 0; gap: 200px; display: flex;"):
    income_totals, expense_totals, total = get_totals(check_data(), date)

    income_chart = ui.echart({
        'title': {'text': f'Income: {round(sum(income_totals.values()), 2)}'},
        'tooltip': {'trigger': 'item'},
        'series': [{
            'type': 'pie',
            'data': [{'name': name, 'value': val} for name, val in income_totals.items()]
            }]
        }).style("width: 350px; height: 300px;")

    total_chart = ui.echart({
        'title': {'text': f'Total: {round(sum(total.values()), 2)}'},
        'tooltip': {'trigger': 'axis'},
        'xAxis': {'type': 'category', 'data': list(total.keys())},
        'yAxis': {'type': 'value'},
        'series': [{
            'type': 'bar',
            'data': [{'value': val, 'itemStyle': {'color': '#91cc75' if val >= 0 else '#ee6666'}} for val in total.values()]
        }]
    }).style("width: 500px; height: 300px;")

    expenses_chart = ui.echart({
        'title': {'text': f'Expenses: {round(sum(expense_totals.values()), 2)}'},
        'tooltip': {'trigger': 'item'},
        'series': [{
            'type': 'pie',
            'data': [{'name': name, 'value': val} for name, val in expense_totals.items()]
            }]
        }).style("width: 350px; height: 300px;")

data = check_data()

if data:
    table = {
        'columnDefs': [
            {'headerName': 'Category', 'field': 'Category'},
            {'headerName': 'Amount', 'field': 'Amount'},
            {'headerName': 'Date', 'field': 'Date'},
            {'headerName': 'Notes', 'field': 'Notes'},
        ],
        'rowData': [],
        'rowSelection': {'mode': 'multiRow'},
    }

    for row in data[::-1]:
        table['rowData'].append(row)

    grid = ui.aggrid(table)

    with ui.row():
        ui.button('Delete', on_click=delete)
        ui.button('Edit', on_click=edit)

ui.run(host='127.0.0.1', port=8080, favicon=icon)
