
import datetime
import cgi
import psycopg2

conn = psycopg2.connect("postgres://qubbkhqdeylkex:28b87a762a0fe1dd841f224df2caa5408c99ffe03fa9b47d60155379ad0e4101@ec2-52-204-157-26.compute-1.amazonaws.com:5432/dfn5omign98a33")
cursor = conn.cursor()

newtable =f"""
    CREATE TABLE IF NOT EXISTS BOARDS(
        ID SERIAL PRIMARY KEY NOT NULL,
        BOARD TEXT NOT NULL
    )
    """

newtable2 = f"""
    CREATE TABLE IF NOT EXISTS USERS(
        ID SERIAL PRIMARY KEY NOT NULL,
        USERNAME TEXT NOT NULL,
        PASSWORD TEXT NOT NULL,
        EMAIL TEXT, 
        DATE TEXT
    )
"""
cursor.execute(newtable)
cursor.execute(newtable2)

conn.commit()
conn.close()