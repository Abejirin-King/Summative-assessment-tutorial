# Taxi Data Flask App

## Overview

This project is a Flask web dashboard that visualizes NYC Taxi Trip data loaded into a MySQL database. It displays average fares, distances, and speeds for trips within a selected date range.

## Prerequisites

Before starting, ensure you have the following installed:

| Tool | Purpose | Version (recommended) |
|------|---------|---------------------|
| Python | Backend runtime | 3.9 or newer |
| MySQL Server | Stores taxi data | 8.0+ |
| pip | Python package manager | latest |
| VS Code | Development IDE | latest |

## Setup Instructions (Use VS Code)

### Step 1:  Download the Project

Downoad the provided zip file, extract it and then open the folder in vscode

### Step 2: Create a Python Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Create the MySQL Database

Run this in your bash terminal:

```bash
mysql -u root -p < setup.sql   #root is your username
```


### Step 5: Load Data into MySQL and Run the app

Run the app in your terminal

```bash
python app.py
```

If successful, you’ll see:

```
 Ensuring DB and table exist...
 Starting CSV -> MySQL load (this may take several minutes for a large file)...
 Inserted 196596 rows (total so far: 196596)
```

Then after it is done loading you should see:

```
* Running on http://127.0.0.1:5000
```

The first time you run the app, it is going to load the csv to mysql so it might take a few minutes. If you want to restart the app after it runs for the first time, in the app.py, on line 19, change LOAD_ON_START to False. 


Then open your browser and visit:

 http://127.0.0.1:5000


