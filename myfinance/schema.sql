DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS data;
DROP TABLE IF EXISTS rules;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  income_cat TEXT NOT NULL DEFAULT '["Salary", "Shares"]',
  expenses_cat TEXT NOT NULL DEFAULT '["Food", "Clothes", "Health", "Dentist", "Fuel", "Car Expenses", "Home Expenses", "Bills", "Taxes", "Insurance", "Travels", "Vacations"]',
  frequencies TEXT NOT NULL DEFAULT '["Daily", "Weekly", "Monthly", "Yearly"]',
  colors_expenses TEXT NOT NULL DEFAULT '["#5070dd", "#ffd10a", "#c23b3b", "#3fbe95", "#785db0", "#ff994d", "#0ca8df", "#b6d634", "#fb628b", "#505372", "#8d6e4f", "#2e7d32", "#c968d6", "#1f3a8a", "#9e9e9e", "#6a1b4d", "#f4a6a6", "#a8d8b9", "#00695c", "#e6c35c", "#4a148c", "#bcaaa4", "#37474f", "#b39ddb", "#90a4ae"]',
  colors_income TEXT NOT NULL DEFAULT '["#2e9e5b", "#3b82f6", "#e75a9b", "#f2b632", "#7c5cd6"]'
);

CREATE TABLE data (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  category TEXT NOT NULL,
  value REAL NOT NULL,
  income BOOL NOT NULL,
  notes TEXT,
  FOREIGN KEY (author_id) REFERENCES user (id)
);

CREATE TABLE rules (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  name TEXT NOT NULL,
  category TEXT NOT NULL,
  value REAL NOT NULL,
  income BOOL NOT NULL,
  notes TEXT,
  frequency TEXT NOT NULL,
  next_date DATE NOT NULL,
  FOREIGN KEY (author_id) REFERENCES user (id)
);
