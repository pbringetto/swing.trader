CREATE DATABASE core;
USE core;

CREATE TABLE trade (
  id BIGINT(8) AUTO_INCREMENT NOT NULL,
  symbol VARCHAR(32),
  time_frame VARCHAR(8),
  last_price FLOAT(7),
  pnl FLOAT(7),
  open_price FLOAT(7),
  close DATETIME,
  close_price FLOAT(7),
  rsi FLOAT(7),
  status_id BIGINT(8),
  date DATETIME DEFAULT CURRENT_TIMESTAMP,
  amount FLOAT(7),
  primary key (id)
);