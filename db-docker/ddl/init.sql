CREATE TABLE IF NOT EXISTS scheduler_tasks (
    id VARCHAR(255) PRIMARY KEY,
    chat_id VARCHAR(255),
    origin VARCHAR(255),
    destination VARCHAR(255),
    depart_date VARCHAR(255),
    depart_time VARCHAR(255),
    interval INT
);

