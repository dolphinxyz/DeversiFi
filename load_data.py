#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import csv
import psycopg2
import pandas as pd
from decouple import AutoConfig
from pathlib import Path

def connect_to_db():
    env_path = search_path=str(Path(__file__).parent) + "/.env"
    config = AutoConfig(env_path)
    base = "host='%s' port=%s dbname='%s' user=%s password=%s"
    full = base % (
        config("DBHOST"),
        config("DBPORT"),
        config("DBNAME"),
        config("DBUSER"),
        config("DBPASSWORD"))
    return psycopg2.connect(full)

def load_registrations(conn):
    df = pd.read_csv("data/registrations.csv")
    df.update(df.applymap("'{}'".format))
    query_values = []
    for index, row in df.iterrows():
        row_values = [
            row["Address"],
            row["Registration date"]
        ]
        row_values_string = ",".join(map(str, row_values))
        query_values.append("(" +  row_values_string  + ")")
    values = ",".join(query_values)
    query = """
        INSERT INTO registrations (
            address,
            registration_date) 
        VALUES """ + values
    cur = conn.cursor()
    cur.execute(query)
    conn.commit()

def load_connected_wallets(conn):
    df = pd.read_csv("data/wallets_connected.csv")
    df.update(df.applymap("'{}'".format))
    query_values = []
    for index, row in df.iterrows():
        row_values = [
            row["Address"],
            row["Date"],
            row["Source"]
        ]
        row_values_string = ",".join(map(str, row_values))
        query_values.append("(" +  row_values_string  + ")")
    values = ",".join(query_values)
    query = """
        INSERT INTO connected_wallets (
            address,
            connection_date,
            source) 
        VALUES """ + values
    cur = conn.cursor()
    cur.execute(query)
    conn.commit()

def load_token_prices(conn):
    df = pd.read_csv("data/token_prices.csv")
    df.update(df.applymap("'{}'".format))
    query_values = []
    for index, row in df.iterrows():
        row_values = [
            row["Token"],
            row["Price in USD"]
        ]
        row_values_string = ",".join(map(str, row_values))
        query_values.append("(" +  row_values_string  + ")")
    values = ",".join(query_values)
    query = """
        INSERT INTO token_prices (
            token,
            price) 
        VALUES """ + values
    cur = conn.cursor()
    cur.execute(query)
    conn.commit()

def load_trades(conn):
    df = pd.read_csv("data/trades.csv")
    df.update(df.applymap("'{}'".format))
    query_values = []
    for index, row in df.iterrows():
        row_values = [
            row["Trade_ID"],
            row["User"],
            row["Pair"],
            row["Amount"]
        ]
        row_values_string = ",".join(map(str, row_values))
        query_values.append("(" +  row_values_string  + ")")
    values = ",".join(query_values)
    query = """
        INSERT INTO trades (
            trade_id,
            address,
            pair,
            amount) 
        VALUES """ + values
    cur = conn.cursor()
    cur.execute(query)
    conn.commit()

def main():
    conn = connect_to_db()
    load_registrations(conn)
    load_connected_wallets(conn)
    load_token_prices(conn)
    load_trades(conn)
    conn.close()

if __name__ == "__main__":
    main()
