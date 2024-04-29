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
