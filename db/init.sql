CREATE DATABASE core;
USE core;

CREATE TABLE `signal_data` (
    id BIGINT(8) AUTO_INCREMENT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    pair VARCHAR(8),
    price  FLOAT(8),
    time_frame INT,
    dev FLOAT(8),
    var FLOAT(8),
    rsi FLOAT(8),
    sma3 FLOAT(8),
    sma3_13_hist FLOAT(8),
    sma8 FLOAT(8),
    sma13 FLOAT(8),
    sma8_13_hist FLOAT(8),
    macd FLOAT(8),
    macd_signal FLOAT(8),
    macd_hist FLOAT(8),
    primary key (id)
);

CREATE TABLE `position` (
    txid VARCHAR(48) NOT NULL,
    closing_txid VARCHAR(48) NOT NULL,
    type VARCHAR(8),
    closed_at DATETIME,
    primary key (txid)
);

CREATE TABLE `order` (
    txid VARCHAR(48) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    pair VARCHAR(8),
    type VARCHAR(8),
    volume FLOAT(8),
    price  FLOAT(8),
    cost FLOAT(8),
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

CREATE TABLE `settings` (
    id BIGINT(8) AUTO_INCREMENT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    setting VARCHAR(32),
    enabled BIT,
    primary key (id)
);

INSERT INTO `settings` (setting, enabled) VALUES ('trading_enabled', 0);
INSERT INTO `settings` (setting, enabled) VALUES ('created_at', 1);