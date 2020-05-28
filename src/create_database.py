"""
File meant to do a manual (one-time) setup of the server database
"""

import mysql.connector as mariadb

DB_USER = "root"
DB_PASS = "password"
DB_NAME = "lmcm"


# Set up the tables of the database if they do not exist yet
def setup_database():
    conn = None

    try:
        conn = mariadb.connect(user=DB_USER, password=DB_PASS, database=DB_NAME)
    except Exception as e:
        print("Could not connect to database to create tables: {}".format(str(e.args)))
        exit(1)

    cursor = conn.cursor()

    cursor.execute("CREATE TABLE IF NOT EXISTS Movies (itemId INTEGER PRIMARY KEY, tmdbId integer, title text, description text, director integer, runtime integer, genre text, releaseYear integer, avgRating float, posterURL text)")
    cursor.execute("CREATE TABLE IF NOT EXISTS Episodes (itemId INTEGER PRIMARY KEY, parentId integer, episode integer, season integer)")
    cursor.execute("CREATE TABLE IF NOT EXISTS TvShows (itemId INTEGER PRIMARY KEY, tmdbId integer, title text, description text, director integer, runtime integer, genre text, releaseYear integer, avgRating float, posterURL text)")
    cursor.execute("CREATE TABLE IF NOT EXISTS Tracks (itemId INTEGER PRIMARY KEY, parentId integer, title text)")
    cursor.execute("CREATE TABLE IF NOT EXISTS Albums (itemId INTEGER PRIMARY KEY, title text, artist text, genre text, releaseYear integer, avgRating float, posterURL text)")
    cursor.execute("CREATE TABLE IF NOT EXISTS Contributors (id INTEGER PRIMARY KEY AUTO_INCREMENT, name text)")
    cursor.execute("CREATE TABLE IF NOT EXISTS StarsIn (id INTEGER PRIMARY KEY AUTO_INCREMENT, contributorId integer, itemId integer, FOREIGN KEY(contributorId) REFERENCES Contributors(id))")
    cursor.execute("CREATE TABLE IF NOT EXISTS Similar (itemId integer PRIMARY KEY, otherItemId1 integer, otherItemId2 integer, otherItemId3 integer, otherItemId4 integer, otherItemId5 integer, otherItemId6 integer, otherItemId7 integer, otherItemId8 integer)")
    cursor.execute("CREATE TABLE IF NOT EXISTS Licenses (licenseId INTEGER PRIMARY KEY AUTO_INCREMENT, licenseKey text, usedClients integer, maxClients integer)")
    cursor.execute("CREATE TABLE IF NOT EXISTS Clients (id INTEGER PRIMARY KEY AUTO_INCREMENT, clientId text, licenseId integer, FOREIGN KEY(licenseId) REFERENCES Licenses(licenseId))")
    cursor.execute("CREATE TABLE IF NOT EXISTS Ratings (id INTEGER PRIMARY KEY AUTO_INCREMENT, clientId text, userId integer, itemId integer, rating float)")

    conn.close()


if __name__ == '__main__':
    setup_database()
