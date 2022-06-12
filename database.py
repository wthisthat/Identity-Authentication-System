import mysql.connector

class Database:

    def __init__(self):
        # check if database exists
        try:
            connection = mysql.connector.connect(host="localhost",user="root",password="1234",database="face_surveillance")
        # create if not exists
        except:
            connect = mysql.connector.connect(host="localhost",user="root",password="1234")
            cur = connect.cursor()
            cur.execute("CREATE DATABASE face_surveillance")
            connection = mysql.connector.connect(host="localhost",user="root",password="1234",database="face_surveillance")
        
        cursor = connection.cursor()
        
        # check table identity
        cursor.execute('''CREATE TABLE IF NOT EXISTS Identity(
            id INT AUTO_INCREMENT NOT NULL PRIMARY KEY, 
            name VARCHAR(255) NOT NULL, 
            gender CHAR(1) NOT NULL,
            encoding BLOB NOT NULL,
            remarks VARCHAR(255) NULL,
            UNIQUE (name))''')
        
        # check table record
        cursor.execute('''CREATE TABLE IF NOT EXISTS Record(
            id INT AUTO_INCREMENT PRIMARY KEY NOT NULL, 
            timestamp TIMESTAMP NOT NULL,
            recognized BOOLEAN NOT NULL,
            distance FLOAT(5,4) NULL,
            identity_id int NULL,
            FOREIGN KEY(identity_id) REFERENCES Identity(id) ON DELETE CASCADE)''')

        cursor.close()
        connection.close()
    
    def connect(self):
        connection = mysql.connector.connect(host="localhost",user="root",password="1234",database="face_surveillance")
        cursor = connection.cursor()
        return connection,cursor

    # query functions for identity table
    def add_identity(self, name, gender, encoding, remarks):
        connection, cursor = self.connect()
        sql = "INSERT INTO Identity (name, gender, encoding, remarks) VALUES (%s,%s,%s,%s)"
        val = (name, gender, encoding, remarks)
        cursor.execute(sql,val)
        connection.commit()
        cursor.close()
        connection.close()

    def load_identity(self):
        connection, cursor = self.connect()
        cursor.execute("SELECT * FROM Identity")
        results = cursor.fetchall()
        cursor.close()
        connection.close()
        return results

    def delete_identity(self, id):
        connection, cursor = self.connect()
        sql = "DELETE FROM Identity WHERE id = %s"
        val = (id,)
        cursor.execute(sql,val)
        connection.commit()
        cursor.close()
        connection.close()

    def edit_identity(self, id, name, gender, encoding, remarks):
        connection, cursor = self.connect()
        sql = "UPDATE Identity SET name = %s, gender = %s, encoding = %s, remarks = %s WHERE id = %s"
        val = (name, gender, encoding, remarks, id)
        cursor.execute(sql,val)
        connection.commit()
        cursor.close()
        connection.close()

    def search_identity(self, name):
        connection, cursor = self.connect()
        sql = "SELECT * FROM Identity WHERE name = %s"
        val = (name,)
        cursor.execute(sql,val)
        result = cursor.fetchall()
        cursor.close()
        connection.close()
        return result

    # query functions for record table
    def add_record(self, timestamp, recognized, distance, identity_id):
        connection, cursor = self.connect()
        sql = "INSERT INTO Record (timestamp, recognized, distance, identity_id) VALUES (%s,%s,%s,%s)"
        val = (timestamp, recognized, distance, identity_id)
        cursor.execute(sql,val)
        connection.commit()
        cursor.close()
        connection.close()
    
    def truncate_record(self):
        connection, cursor = self.connect()
        cursor.execute("TRUNCATE TABLE Record")
        connection.commit()
        cursor.close()
        connection.close()
    
    def load_record(self):
        connection, cursor = self.connect()
        cursor.execute("SELECT r.*, i.name FROM Record r LEFT JOIN Identity i ON r.identity_id = i.id")
        results = cursor.fetchall()
        cursor.close()
        connection.close()
        return results

    # def latest_record(self, name):
    #     connection, cursor = self.connect()
    #     sql = "SELECT r.timestamp FROM Record r INNER JOIN Identity i ON r.identity_id = i.id \
    #         WHERE i.name = %s ORDER BY timestamp DESC LIMIT 1"
    #     val = (name,)
    #     cursor.execute(sql,val)
    #     results = cursor.fetchall()
    #     cursor.close()
    #     connection.close()
    #     return results
    
    

# connect = mysql.connector.connect(host="localhost",user="root",password="1234",database="face_surveillance")
# cur = connect.cursor()
# cur.execute("DROP TABLE IDENTITY")
# connect.close()
# cur.close()