# MyFinance

**Simple personal finance tracker with interactive charts.**

Money Manager is a lightweight desktop/web application built with NiceGUI that allows you to track income and expenses, categorize transactions, and visualize your financial data with charts. Everything is stored locally in a JSON file — no accounts, no cloud, just your data.

<p align="center">
  <br>
  <img width="500" height="500" alt="image" src="https://github.com/user-attachments/assets/12870a7d-fd43-42e1-bfcc-407e5e05610b" /><br>


  <img src="https://img.shields.io/badge/License-MIT%202.0-blue.svg" alt="License">
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey.svg" alt="Platform">
  <img src="https://img.shields.io/badge/python-3.11+-blue.svg" alt="Python">
</p>

## Features

- **Income & expense tracking:** Easily add and categorize transactions
- **Receipt upload functionality:** Upload your receips and add the expenses 
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
cd MyFinance/MyFinance
```

2. Create a virtual environment and install nicegui
```bash
python3 -m venv MyFinance-venv
```

On Windows:
```bash
MyFinance-venv\Scripts\activate
pip3 install nicegui requests
```

On Linux:
```bash
source MyFinance-venv/bin/activate
pip3 install nicegui requests
```

3. Run the application
```bash
python3 main.py
```

## Usage

<img width="2832" height="1694" alt="usage" src="https://github.com/user-attachments/assets/6a8c99f0-158e-472d-b8b0-219cd426e396" />

### Adding Income

1. Select a category (e.g. Salary, Investments)
2. Enter an amount
3. (Optional) Add notes
4. Click Save

<img width="2832" height="1694" alt="income" src="https://github.com/user-attachments/assets/42a14e60-c8b1-4ba5-ad4c-2c94259c66c9" />


### Adding Expenses

1. Select a category (e.g. Shopping, Transport)
2. Enter an amount
3. (Optional) Add notes
4. Click Save

<img width="2832" height="1692" alt="expenses" src="https://github.com/user-attachments/assets/04be04f6-d773-4c05-b12f-504ec4410d4a" />

### Uploading a receipt
1. Press the '+' button on the upper-right corner
2. Select the file of the receipt or take a photo (on android)
3. Press the cloud button on the upper-right corner

<img width="574" height="660" alt="Screenshot From 2026-06-12 20-53-19" src="https://github.com/user-attachments/assets/03eec963-69a0-4e9d-b062-29a6925c4e43" />
<img width="574" height="660" alt="Screenshot From 2026-06-12 21-00-08" src="https://github.com/user-attachments/assets/f401febf-e357-45f1-bb06-07abd29219b9" />


After the upload, a pop-up will notify you if the entry was added successfully. If not, try taking another picture of the receipt and make sure the 'TOTAL' is visible
By default, this functionality adds an entry to the "Food" category, but you can change it later.

**Privacy Note:**
The receipt image is securely uploaded to the **OCR.space API** (`https://api.ocr.space/parse/image`) to automatically extract the text and total amount.

According to OCR.space's <a href="https://ocr.space/privacypolicy">Privacy Policy</a>:
- **No Data Retention:** All uploaded files and extracted text are **deleted immediately** after processing is complete. The service does not store, archive, or retain any of your data .

### Managing Entries

- **Delete:** Select one or more rows and click Delete
- **Edit:** Select a row and click Edit

<img width="2832" height="554" alt="managing" src="https://github.com/user-attachments/assets/a154e761-eae4-43fa-9227-0613961af229" />


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
### API
https://ocr.space/ocrapi

## Project Structure

```
MyFinance/
├── main.py             # Main application logic and UI
├── data.json           # Data storage (auto-created)
├── icon.png            # Default Image
├── icon.ico            # Icon
├── receipt.jpg         # Copy of uploaded receipt (if it's uploaded)
└── README.md           # Documentation
```

## Dependencies

```
nicegui
requests
```

## Disclaimer

This software is provided "as is" without warranty of any kind. The developer is not responsible for data loss, or incorrect financial calculations.

## Deployment

MyFinance is designed to run locally or on a home server for continuous access.

A recommended setup is running the application on a **Proxmox server** (or any Linux server), allowing you to access your finance dashboard from any device on your network.
If you decide to do so, update the last line in main.py with your server’s IP.
Save and restart the app to apply the change.
