# MyFinance

**Simple personal finance tracker with interactive charts.**

Money Manager is a lightweight desktop/web application built with NiceGUI that allows you to track income and expenses, categorize transactions, and visualize your financial data with charts. Everything is stored locally in a JSON file — no accounts, no cloud, just your data.

<p align="center">
  <br>
  <img width="500" height="500" alt="image" src="https://github.com/user-attachments/assets/12870a7d-fd43-42e1-bfcc-407e5e05610b" /><br>


  <img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg" alt="License">
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey.svg" alt="Platform">
  <img src="https://img.shields.io/badge/python-3.11+-blue.svg" alt="Python">
</p>

## Features

- **Income & expense tracking:** Easily add and categorize transactions
- **Custom categories:** Separate categories for income and expenses
- **Interactive charts:**
  - Income distribution (pie chart)
  - Expense distribution (pie chart)
  - Total balance per category (bar chart)
- **Edit & delete entries:** Full control over your data
- **Local storage:** Data is saved in a JSON file
- **Minimal UI:** Clean and simple interface using NiceGUI

## Quick Start

### Prerequisites

- Python 3.11 or higher

### Installation

1. Clone the repository
   
Open a terminal in your home directory and type:
```bash
git clone https://github.com/Lif28/MyFinance.git
cd MyFinance
```

2. Create a virtual environment and install nicegui
```bash
python3 -m venv MyFinance-venv
```

On Windows:
```bash
MyFinance-venv\Scripts\activate
pip3 install nicegui
```

On Linux:
```bash
source MyFinance-venv/bin/activate
pip3 install nicegui
```

3. Run the application
```bash
python3 main.py
```

## Usage

<img width="1899" height="950" alt="image" src="https://github.com/user-attachments/assets/3799c47e-0211-4ca8-b147-890572241a1a" />


### Adding Income

1. Select a category (e.g. Salary, Investments)
2. Enter an amount
3. (Optional) Add notes
4. Click Save

<img width="1899" height="950" alt="image" src="https://github.com/user-attachments/assets/9cee8d2e-e508-4ecb-b8de-7008153fda93" />

### Adding Expenses

1. Select a category (e.g. Shopping, Transport)
2. Enter an amount
3. (Optional) Add notes
4. Click Save

<img width="1899" height="950" alt="image" src="https://github.com/user-attachments/assets/29b24bb7-05ce-4599-a317-82d02b6834f5" />


### Managing Entries

- **Delete:** Select one or more rows and click Delete
- **Edit:** Select a row and click Edit

<img width="1906" height="354" alt="image" src="https://github.com/user-attachments/assets/2a960e4d-149d-4fde-9275-03a6d78024f9" />


### Charts

The application provides three real-time charts:

- **Income Pie Chart:** distribution of income sources
- **Expense Pie Chart:** distribution of expenses
- **Total Bar Chart:** total of income - expenses

## How It Works

### Data Storage

All data is stored locally in a JSON file:

```
MyFinance/data.json
```
Each entry has the following structure:

```
{
  "Category": "Shopping",
  "Amount": "75",
  "Notes": "Shoes",
  "Date": "2026-04-01 16:45:00"
}
```

## Project Structure

```
MyFinance/
├── main.py             # Main application logic and UI
├── data.json           # Data storage (auto-created)
├── icon.png            # Default Image
├── icon.ico            # Icon
└── README.md           # Documentation
```

## Dependencies

```
nicegui
```

## Disclaimer

This software is provided "as is" without warranty of any kind. The developer is not responsible for data loss, or incorrect financial calculations.

## Deployment

MyFinance is designed to run locally or on a home server for continuous access.

A recommended setup is running the application on a **Proxmox server** (or any Linux server), allowing you to access your finance dashboard from any device on your network.
