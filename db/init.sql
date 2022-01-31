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
  date DATETIME DEFAULT CURRENT_TIMESTAMP,
  amount FLOAT(7),
  position VARCHAR(8),
  fee FLOAT(7),
  primary key (id)
);

CREATE TABLE historic_data (
  id BIGINT(8) AUTO_INCREMENT NOT NULL,
  symbol VARCHAR(32),
  close_time int(11),
  open_price FLOAT(7),
  high_price FLOAT(7),
  low_price FLOAT(7),
  close_price FLOAT(7),
  volume FLOAT(7),
  quote_volume FLOAT(7),
  time_frame INT(7),
  primary key (id),
  unique key `symbol_close_time` (`symbol`,`close_time`)
);

CREATE TABLE signal_data (
  id BIGINT(8) AUTO_INCREMENT NOT NULL,
  symbol VARCHAR(32),
  time_frame VARCHAR(8),
  rsi FLOAT(7),
  sma200 FLOAT(7),
  sma14 FLOAT(7),
  macd FLOAT(7),
  macd_signal FLOAT(7),
  macd_hist FLOAT(7),
  bid_volume FLOAT(7),
  ask_volume FLOAT(7),
  bid_price FLOAT(7),
  ask_price FLOAT(7),
  bollinger_down FLOAT(7),
  bollinger_up FLOAT(7),
  date DATETIME DEFAULT CURRENT_TIMESTAMP,
  primary key (id)
);

CREATE TABLE trade_signal_data (
  trade_id BIGINT(8),
  signal_data_id BIGINT(8),
  date DATETIME DEFAULT CURRENT_TIMESTAMP,
  primary key (trade_id, signal_data_id)
);

CREATE TABLE trade_signal_settings (
  trade_id BIGINT(8),
  signal_data_id BIGINT(8),
  date DATETIME DEFAULT CURRENT_TIMESTAMP,
  primary key (trade_id, signal_data_id)
);