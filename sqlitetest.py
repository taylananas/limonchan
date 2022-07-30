import sqlite3
import datetime
connection = sqlite3.connect("testdatabase.db")


def tableolustur():
    conn = connection.cursor()
    randomvariable = f"""
            CREATE TABLE kullanicilar (            
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT  NOT NULL,
            para INTEGER NOT NULL)
            date TEXT  NOT NULL,
    """
    conn.execute(randomvariable)
    connection.commit()
    conn.close()

def yenikullanici():
    conn = connection.cursor()
    isim = input("Isim:")
    para = int(input("Para:"))
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    yenikullanicitext = f"INSERT INTO kullanicilar (name, date, para) VALUES ('{isim}', '{date}', '{para}') "
    conn.execute(yenikullanicitext)
    connection.commit()
    conn.close()

def withdraw():
    conn = connection.cursor()
    conn.row_factory = sqlite3.Row
    isim = input("Isim: ")
    selectkisi = f"SELECT * FROM kullanicilar WHERE name = '{isim}'"
    people = conn.execute(selectkisi).fetchall()
    for i in people:
        print("Mevcut Para: ",i["para"])
        tutar = int(input("Çekilecek Para: "))
        komut = f"UPDATE kullanicilar SET para = {i['para']-tutar} WHERE name = '{i['name']}'"
        print(f"Kalan Para: {i['para']-tutar}")
        conn.execute(komut)
    connection.commit()
    conn.close()

withdraw()