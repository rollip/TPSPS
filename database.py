import mysql.connector
from mysql.connector import Error


class Database:
    def __init__(self, host="localhost", user="root", password="password", database="mydatabase"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                print("Connected to MySQL database")
        except Error as e:
            print("Error while connecting to MySQL", e)

    def close(self):
        if self.connection.is_connected():
            self.connection.close()
            print("MySQL connection closed")


class Scheduler:
    def __init__(self, db):
        self.db = db

    def create_sheduler(self):
        query = 'DELIMITER $$ CREATE EVENT delete_old_accidents_event ON SCHEDULE EVERY 1 HOUR DO BEGIN DELETE FROM RiskAccident WHERE TIMESTAMPDIFF(HOUR, created_at, NOW()) >= 1; END$$ DELIMITER ;'
        cursor = self.db.connection.cursor()
        cursor.execute(query)
        self.db.connection.commit()
        print("Scheduler created")


class RiskAccident:
    def __init__(self, db, ngsa_id, mo_identifier, perceived_severity, displayed_text, probability):
        self.db = db
        self.ngsa_id = ngsa_id
        self.mo_identifier = mo_identifier
        self.perceived_severity = perceived_severity
        self.displayed_text = displayed_text
        self.probability = probability

    def delete_old_risks(self, mo_identifier):
        try:
            cursor = self.db.connection.cursor()
            query = "DELETE FROM RiskAccident WHERE mo_identifier = %s"
            cursor.execute(query, (mo_identifier,))
            self.db.connection.commit()
            print("Old risks deleted for MO_identifier:", mo_identifier)
        except Error as e:
            print("Error while deleting old risks:", e)

    def save_to_database(self):
        try:
            cursor = self.db.connection.cursor()
            query = "INSERT INTO RiskAccident (ngsa_id, mo_identifier, perceived_severity, displayed_text, probability) VALUES (%s, %s, %s, %s, %s)"
            values = (self.ngsa_id, self.mo_identifier, self.perceived_severity, self.displayed_text, self.probability)
            cursor.execute(query, values)
            self.db.connection.commit()
            print("RiskAccident saved to database successfully")
        except Error as e:
            print("Error while saving RiskAccident to database", e)

    def delete_from_database(self):
        try:
            cursor = self.db.connection.cursor()
            query = "DELETE FROM RiskAccident WHERE ngsa_id = %s"
            value = (self.ngsa_id,)
            cursor.execute(query, value)
            self.db.connection.commit()
            print("RiskAccident deleted from database successfully")
        except Error as e:
            print("Error while deleting RiskAccident from database", e)


