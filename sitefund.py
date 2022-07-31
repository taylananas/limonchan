from unittest import result
from django.shortcuts import render
from flask import Flask, request, render_template, url_for, flash, redirect
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
import datetime
import psycopg2
import pandas as pd
import pandas.io.sql as psql

#postgres://qubbkhqdeylkex:28b87a762a0fe1dd841f224df2caa5408c99ffe03fa9b47d60155379ad0e4101@ec2-52-204-157-26.compute-1.amazonaws.com:5432/dfn5omign98a33
#"dbname=postgres user=postgres password=Aukors123"
def get_db_connection():
    connect = psycopg2.connect("dbname=postgres user=postgres password=Aukors123")
    connect = psycopg2.connect("postgres://qubbkhqdeylkex:28b87a762a0fe1dd841f224df2caa5408c99ffe03fa9b47d60155379ad0e4101@ec2-52-204-157-26.compute-1.amazonaws.com:5432/dfn5omign98a33")
    conn = connect.cursor()
    return connect,conn

def deleteuser(name):
    connect, conn = get_db_connection()
    command = f"""DELETE FROM USERS WHERE username = '{name}'"""
    conn.execute(command)
    connect.commit()
    connect.close()

def deleteboard(board):
    connect, conn = get_db_connection()    
    command = f"DELETE FROM BOARDS WHERE board = '{board}'"
    conn.execute(command)
    command2 = f"DROP TABLE {board}"
    conn.execute(command2)
    connect.commit()
    connect.close()

def gettables():
    connect, conn = get_db_connection()
    conn.execute("""SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public'""")
    tables = []
    tabletuple = conn.fetchall()
    for i in tabletuple:
        tables.append(i[0])
    connect.close()
    return tables

def table(tablename):
    connect, conn = get_db_connection()
    tabletuple = gettables()
    tables = []
    for i in tabletuple:
        tables.append(i[0])
    my_table    = psql.read_sql(f'select * from {tablename}', connect)   
    connect.close()
    return my_table

def altering(tablename,columnname):
    connect, conn = get_db_connection()
    conn.execute(f"ALTER TABLE {tablename} ADD {columnname} TEXT")
    connect.commit()
    connect.close()

def updatetable(tablename, creator, boardname):
    connect, conn = get_db_connection()
    conn.execute(f"UPDATE {tablename} SET CREATOR = '{creator}' WHERE board = '{boardname}'")
    connect.commit()
    connect.close()

def makeadmin(username):
    connect, conn = get_db_connection()
    conn.execute(f"UPDATE users SET isadmin = 'yes' WHERE username = '{username}'")
    connect.commit()
    connect.close()


print(table("boards"))