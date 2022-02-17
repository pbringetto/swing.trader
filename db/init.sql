CREATE DATABASE core;
USE core;

CREATE TABLE `order` (
    id BIGINT(8) AUTO_INCREMENT NOT NULL,
    createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    order_id VARCHAR(48),
    symbol VARCHAR(8),
    time_frame INT,
    status VARCHAR(8),
    primary key (id),
    unique key `symbol_close_time_time_frame` (`order_id`)
);

CREATE TABLE `position` (
    id BIGINT(8) AUTO_INCREMENT NOT NULL,
    createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    symbol VARCHAR(32),
    time_frame INT,
    closedAt DATETIME,
    primary key (id)
);