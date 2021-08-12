CREATE TABLE connected_wallets (
  id serial primary key,
  address text,
  connection_date text,
  source text
);

CREATE TABLE registrations (
  id serial primary key,
  address text,
  registration_date text,
  source text
);

CREATE TABLE token_prices (
  id serial primary key,
  token text,
  price numeric,
  source text
);

CREATE TABLE trades (
  id serial primary key,
  trade_id text,
  address text,
  pair text,
  amount numeric,
  source text,
  price numeric,
  volume numeric
);

