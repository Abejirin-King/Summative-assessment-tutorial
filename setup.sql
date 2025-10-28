CREATE DATABASE IF NOT EXISTS summative_ass;
USE summative_ass;
CREATE USER 'main_user'@'localhost' IDENTIFIED BY 'King40$$';
GRANT ALL PRIVILEGES ON summative_ass.* TO 'main_user'@'localhost';
FLUSH PRIVILEGES;

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
