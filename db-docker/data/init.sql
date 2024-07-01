CREATE SCHEMA kai_notif;

CREATE TABLE IF NOT EXISTS kai_notif.scheduler_tasks (
    id TEXT PRIMARY KEY,
    chat_id TEXT NOT NULL,
    origin TEXT,
    destination TEXT,
    depart_date TEXT,
    depart_time TEXT,
    interval_scheduler INTEGER,
    status TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL
);

CREATE TABLE IF NOT EXISTS kai_notif.stations (
    code VARCHAR(10) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    city VARCHAR(255) NOT NULL,
    cityname VARCHAR(255) NOT NULL
);

COPY kai_notif.stations
FROM '/docker-entrypoint-initdb.d/list_stations.csv'
DELIMITER ','
CSV HEADER;