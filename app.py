import os
import pandas as pd
import numpy as np
import math
from flask import Flask, jsonify
import mysql.connector
from mysql.connector import errorcode


CSV_FILE = "cleaned_data.csv"   
MYSQL_CONFIG = {
    "host": "localhost",
    "user": "main_user",
    "password": "King40$$",
    "database": "summative_ass",
    "autocommit": False
}
CHUNK_SIZE = 200000
LOAD_ON_START = True

app = Flask(__name__, static_folder="static", template_folder="static")

def get_connection():
    return mysql.connector.connect(**MYSQL_CONFIG)

def ensure_db_and_table():
    tmp_conf = MYSQL_CONFIG.copy()
    tmp_db = tmp_conf.pop("database")
    conn = mysql.connector.connect(
        host=tmp_conf["host"],
        user=tmp_conf["user"],
        password=tmp_conf["password"]
    )
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {tmp_db};")
    conn.commit()
    cursor.close()
    conn.close()

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS trips (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        VendorID INT,
        pickup_datetime DATETIME,
        dropoff_datetime DATETIME,
        passenger_count INT,
        trip_distance FLOAT,
        RatecodeID INT,
        PULocationID INT,
        DOLocationID INT,
        payment_type VARCHAR(64),
        fare_amount FLOAT,
        extra FLOAT,
        mta_tax FLOAT,
        tip_amount FLOAT,
        tolls_amount FLOAT,
        improvement_surcharge FLOAT,
        total_amount FLOAT,
        trip_duration_min FLOAT,
        trip_speed_kmph FLOAT,
        fare_per_km FLOAT,
        tip_percent FLOAT
    );
    """)
    conn.commit()
    cursor.close()
    conn.close()

def clean_chunk(df):
    df = df.dropna(subset=['tpep_pickup_datetime', 'tpep_dropoff_datetime'])
    df['pickup_datetime'] = pd.to_datetime(df['tpep_pickup_datetime'], errors='coerce')
    df['dropoff_datetime'] = pd.to_datetime(df['tpep_dropoff_datetime'], errors='coerce')

    if 'trip_duration_min' not in df.columns:
        df['trip_duration_min'] = (df['dropoff_datetime'] - df['pickup_datetime']).dt.total_seconds() / 60

    df = df[df['trip_duration_min'] > 0]

    df['trip_speed_kmph'] = (
        df['trip_distance'] / (df['trip_duration_min'] / 60.0)
    ).replace([float('inf'), -float('inf')], np.nan)

    df = df[(df['trip_speed_kmph'] > 0) & (df['trip_speed_kmph'] < 150)]

    df['fare_per_km'] = df['fare_amount'] / df['trip_distance'].replace(0, np.nan)
    df['tip_percent'] = (df['tip_amount'] / df['fare_amount'].replace(0, np.nan)) * 100

    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.fillna(0)

    return df


def load_csv_to_mysql():
    if not os.path.exists(CSV_FILE):
        raise FileNotFoundError(
            f"CSV file not found at {CSV_FILE}. Please place your cleaned_data.csv in the project root."
        )

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("TRUNCATE TABLE trips;")
    conn.commit()

    reader = pd.read_csv(CSV_FILE, chunksize=CHUNK_SIZE, low_memory=True)
    total = 0

    for chunk in reader:
        chunk.columns = [c.strip() for c in chunk.columns]

        mapping = {
            'VendorID':'VendorID',
            'tpep_pickup_datetime':'tpep_pickup_datetime',
            'tpep_dropoff_datetime':'tpep_dropoff_datetime',
            'passenger_count':'passenger_count',
            'trip_distance':'trip_distance',
            'RatecodeID':'RatecodeID',
            'PULocationID':'PULocationID',
            'DOLocationID':'DOLocationID',
            'payment_type':'payment_type',
            'fare_amount':'fare_amount',
            'extra':'extra',
            'mta_tax':'mta_tax',
            'tip_amount':'tip_amount',
            'tolls_amount':'tolls_amount',
            'improvement_surcharge':'improvement_surcharge',
            'total_amount':'total_amount',
            'trip_duration_min':'trip_duration_min'
        }

        for k in mapping.values():
            if k not in chunk.columns:
                chunk[k] = pd.NA

        cleaned = clean_chunk(chunk)
        insert_rows = []

        for _, r in cleaned.iterrows():
            insert_rows.append(tuple([
                int(r.get('VendorID')) if pd.notna(r.get('VendorID')) else None,
                r.get('pickup_datetime').to_pydatetime() if pd.notna(r.get('pickup_datetime')) else None,
                r.get('dropoff_datetime').to_pydatetime() if pd.notna(r.get('dropoff_datetime')) else None,
                int(r.get('passenger_count')) if pd.notna(r.get('passenger_count')) else None,
                float(r.get('trip_distance')) if pd.notna(r.get('trip_distance')) else None,
                int(r.get('RatecodeID')) if pd.notna(r.get('RatecodeID')) else None,
                int(r.get('PULocationID')) if pd.notna(r.get('PULocationID')) else None,
                int(r.get('DOLocationID')) if pd.notna(r.get('DOLocationID')) else None,
                r.get('payment_type') if pd.notna(r.get('payment_type')) else None,
                float(r.get('fare_amount')) if pd.notna(r.get('fare_amount')) else None,
                float(r.get('extra')) if pd.notna(r.get('extra')) else None,
                float(r.get('mta_tax')) if pd.notna(r.get('mta_tax')) else None,
                float(r.get('tip_amount')) if pd.notna(r.get('tip_amount')) else None,
                float(r.get('tolls_amount')) if pd.notna(r.get('tolls_amount')) else None,
                float(r.get('improvement_surcharge')) if pd.notna(r.get('improvement_surcharge')) else None,
                float(r.get('total_amount')) if pd.notna(r.get('total_amount')) else None,
                float(r.get('trip_duration_min')) if pd.notna(r.get('trip_duration_min')) else None,
                float(r.get('trip_speed_kmph')) if pd.notna(r.get('trip_speed_kmph')) else None,
                float(r.get('fare_per_km')) if pd.notna(r.get('fare_per_km')) else None,
                float(r.get('tip_percent')) if pd.notna(r.get('tip_percent')) else None
            ]))

        if insert_rows:
            insert_sql = """
            INSERT INTO trips (
                VendorID,pickup_datetime,dropoff_datetime,passenger_count,trip_distance,RatecodeID,
                PULocationID,DOLocationID,payment_type,fare_amount,extra,mta_tax,tip_amount,tolls_amount,
                improvement_surcharge,total_amount,trip_duration_min,trip_speed_kmph,fare_per_km,tip_percent
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """
            cursor.executemany(insert_sql, insert_rows)
            conn.commit()
            total += len(insert_rows)
            print(f"Inserted {len(insert_rows)} rows (total so far: {total})")

    cursor.close()
    conn.close()
    print("CSV load complete. Total rows inserted:", total)

@app.route("/api/overview")
def overview():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
            COUNT(*) AS total_trips,
            SUM(total_amount) AS total_revenue,
            AVG(fare_amount) AS avg_fare,
            AVG(trip_distance) AS avg_distance,
            AVG(trip_duration_min) AS avg_duration,
            AVG(tip_percent) AS avg_tip
        FROM trips
    """)
    data = cursor.fetchone()
    cursor.close()
    conn.close()
    return jsonify(data)

@app.route("/api/payment_distribution")
def payment_distribution():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT payment_type, COUNT(*) AS count FROM trips GROUP BY payment_type")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    result = [{"payment_type": r[0] if r[0] else "UNKNOWN", "count": int(r[1])} for r in rows]
    return jsonify(result)

@app.route("/api/trip_distance_distribution")
def trip_distance_distribution():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            CASE 
                WHEN trip_distance < 2 THEN '0-2'
                WHEN trip_distance >=2 AND trip_distance < 5 THEN '2-5'
                WHEN trip_distance >=5 AND trip_distance < 10 THEN '5-10'
                WHEN trip_distance >=10 AND trip_distance < 20 THEN '10-20'
                ELSE '20+' 
            END AS distance_range,
            COUNT(*) AS count
        FROM trips
        GROUP BY distance_range
        ORDER BY FIELD(distance_range, '0-2','2-5','5-10','10-20','20+')
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    result = [{"distance_range": r[0], "count": int(r[1])} for r in rows]
    return jsonify(result)

@app.route("/")
def index():
    return app.send_static_file("index.html")

if __name__ == "__main__":
    print("Ensuring DB and table exist...")
    ensure_db_and_table()
    if LOAD_ON_START:
        print("Starting CSV -> MySQL load (this may take several minutes for a large file)...")
        load_csv_to_mysql()
    print("Starting Flask app...")
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)

