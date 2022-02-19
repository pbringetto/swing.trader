CREATE DATABASE core;
USE core;

CREATE TABLE `order` (
    txid VARCHAR(48) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    pair VARCHAR(8),
    time_frame INT,
    status VARCHAR(8),
    closed_at DATETIME,
    primary key (txid)
);

CREATE TABLE `trade` (
    txid VARCHAR(48) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    pair VARCHAR(32),
    cost FLOAT(8),
    fee FLOAT(8),
    price FLOAT(8),
    closed_at DATETIME,
    primary key (txid)
);