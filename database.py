import mysql.connector
from mysql.connector import Error
import logging


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)


class Database:
    def __init__(self, host="localhost", user="root", password="password", database="mydatabase"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection_pool = None

    def connect(self):
        try:
            self.connection_pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="mypool",
                pool_size=5,
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            logging.info("Connected to MySQL database with connection pool")
        except Error as e:
            logging.error("Error while connecting to MySQL", exc_info=e)

    def get_connection(self):
        return self.connection_pool.get_connection()

    def close(self):
        if self.connection_pool:
            self.connection_pool.close()
            logging.info("MySQL connection pool closed")


class Scheduler:
    def __init__(self, db):
        self.db = db

    def create_scheduler(self):
        query = '''CREATE EVENT IF NOT EXISTS delete_old_accidents_event 
                   ON SCHEDULE EVERY 1 HOUR 
                   DO BEGIN 
                       DELETE FROM RiskAccident WHERE TIMESTAMPDIFF(HOUR, created_at, NOW()) >= 1; 
                   END;'''
        try:
            connection = self.db.get_connection()
            cursor = connection.cursor()
            cursor.execute(query)
            connection.commit()
            logging.info("Scheduler created")
        except Error as e:
            logging.error("Error while creating scheduler", exc_info=e)
        finally:
            cursor.close()
            connection.close()


class RiskAccident:
    def __init__(self, db, ngsa_id, mo_identifier, perceived_severity, displayed_text, probability):
        self.db = db
        self.ngsa_id = ngsa_id
        self.mo_identifier = mo_identifier
        self.perceived_severity = perceived_severity
        self.displayed_text = displayed_text
        self.probability = probability

    @staticmethod
    def delete_old_risks(db, mo_identifier):
        try:
            connection = db.get_connection()
            cursor = connection.cursor()
            query = "DELETE FROM RiskAccident WHERE mo_identifier = %s"
            cursor.execute(query, (mo_identifier,))
            connection.commit()
            logging.info("Old risks deleted for MO_identifier: %s", mo_identifier)
        except Error as e:
            logging.error("Error while deleting old risks:", exc_info=e)
        finally:
            cursor.close()
            connection.close()

    def save_to_database(self):
        try:
            connection = self.db.get_connection()
            cursor = connection.cursor()
            query = "INSERT INTO RiskAccident (ngsa_id, mo_identifier, perceived_severity, displayed_text, probability) VALUES (%s, %s, %s, %s, %s)"
            values = (self.ngsa_id, self.mo_identifier, self.perceived_severity, self.displayed_text, self.probability)
            cursor.execute(query, values)
            connection.commit()
            logging.info("RiskAccident saved to database successfully")
        except Error as e:
            logging.error("Error while saving RiskAccident to database", exc_info=e)
        finally:
            cursor.close()
            connection.close()

    def delete_from_database(self):
        try:
            connection = self.db.get_connection()
            cursor = connection.cursor()
            query = "DELETE FROM RiskAccident WHERE ngsa_id = %s"
            cursor.execute(query, (self.ngsa_id,))
            connection.commit()
            logging.info("RiskAccident deleted from database successfully")
        except Error as e:
            logging.error("Error while deleting RiskAccident from database", exc_info=e)
        finally:
            cursor.close()
            connection.close()