from django.shortcuts import render
from flask import Flask, request, render_template, url_for, flash, redirect
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
import datetime
import psycopg2

#postgres://qubbkhqdeylkex:28b87a762a0fe1dd841f224df2caa5408c99ffe03fa9b47d60155379ad0e4101@ec2-52-204-157-26.compute-1.amazonaws.com:5432/dfn5omign98a33
#"dbname=postgres user=postgres password=Aukors123"
def get_db_connection():
    connect = psycopg2.connect("postgres://qubbkhqdeylkex:28b87a762a0fe1dd841f224df2caa5408c99ffe03fa9b47d60155379ad0e4101@ec2-52-204-157-26.compute-1.amazonaws.com:5432/dfn5omign98a33")
    conn = connect.cursor()
    return connect,conn

def deleteuser(name):
    connect, conn = get_db_connection()
    command = f"""DELETE FROM USERS WHERE username = '{name}'"""
    conn.execute(command)
    connect.commit()
    connect.close()



nameuser = input("Name: ")
deleteuser(nameuser)

