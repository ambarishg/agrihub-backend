from config.configs import CONFIGS
from db.sqlite.sqlitehelper import SQLiteDatabaseHelper
from db.mysql.mysqlhelper import MySQLHelper
import datetime 
from itsdangerous import URLSafeTimedSerializer
from UserManager.email_config import *
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class UserManager:
    def __init__(self):
        self.db_type = CONFIGS.DB_TYPE
        
        self.secret_key = CONFIGS.SECRET_KEY
        self.salt = CONFIGS.SALT
        self.serializer = URLSafeTimedSerializer(CONFIGS.SECRET_KEY)

        if self.db_type == "SQLITE":
            self.database_file = CONFIGS.DATABASE_FILE
            self.db_helper = SQLiteDatabaseHelper(self.database_file)
            
        if self.db_type == "MYSQL":
            self.db_helper = MySQLHelper(host = CONFIGS.HOST,
                                         user = CONFIGS.USERNAME_MYSQL,
                                         password=CONFIGS.PASSWORD,
                                         database="BEES")

    def query_helper(self,query):

        if self.db_type == "DUCKDB" or self.db_type == "SQLITE":
            query = query.replace('%s', '?')
        
        return(query)
    
    def check_valid_user(self,
                         email_address,
                         password):
        
        SQL_QUERY = """ 
        SELECT 
        USERS.EMAIL_ADDRESS,
        USERS_ROLE.ROLE_NAME
        FROM 
        USERS INNER JOIN USERS_ROLE
        ON USERS.EMAIL_ADDRESS = USERS_ROLE.EMAIL_ADDRESS
        WHERE USERS.EMAIL_ADDRESS = %s
        AND USERS.PASSWORD = %s
        """

        data = (email_address,password)

        SQL_QUERY = self.query_helper(SQL_QUERY)

        self.db_helper.connect()

        records = self.db_helper.fetch_all(SQL_QUERY,data)
        self.db_helper.close_connection()

        if(len(records) > 0):
            return(records[0][1])
        else:
            return None
        
    def check_valid_user_with_email_address(self,
                         email_address):
        
        SQL_QUERY = """ 
        SELECT 
        USERS.EMAIL_ADDRESS,
        USERS_ROLE.ROLE_NAME
        FROM 
        USERS INNER JOIN USERS_ROLE
        ON USERS.EMAIL_ADDRESS = USERS_ROLE.EMAIL_ADDRESS
        WHERE USERS.EMAIL_ADDRESS = %s
        """

        
        print(email_address)

        SQL_QUERY = self.query_helper(SQL_QUERY)

        self.db_helper.connect()

        records = self.db_helper.fetch_all(SQL_QUERY,[email_address])
        self.db_helper.close_connection()

        if(len(records) > 0):
            return(records[0][1])
        else:
            return None
    
        
        
    def register_user(self,
                      user_name,
                      email_address,
                      password,
                      confirm_password,
                      locations):
        
        if password != confirm_password:
            return ("ERROR_PASSWORD_MISMATCH")
        
        INSERT_QUERY=""" 
        INSERT INTO USERS
        (
        USERNAME,
        PASSWORD,
        EMAIL_ADDRESS,
        CREATED_BY,
        CREATED_AT,
        UPDATED_BY,
        UPDATED_AT
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s)
        """
        data = (user_name,
        password,
        email_address,
        "ADMIN",
        datetime.datetime.now(),
        "ADMIN",
        datetime.datetime.now()
        )

        try:
            # Execute the insert query with the provided data
            self.db_helper.connect()
            insert_query = self.query_helper(INSERT_QUERY)
            self.db_helper.execute_query(insert_query, data)
            print("USERS record inserted successfully.")
        except Exception as e:
            print(f"An error occurred: {e}")
            raise Exception(e)
        finally:
            # Ensure the database connection is closed
            self.db_helper.close_connection()
        
        INSERT_QUERY=""" 
        INSERT INTO USERS_ROLE
        (
        EMAIL_ADDRESS,
        ROLE_NAME,
        CREATED_BY,
        CREATED_AT,
        UPDATED_BY,
        UPDATED_AT
        )
        VALUES (%s,%s,%s,%s,%s,%s)
        """

        data = (email_address,
                "USER",
                "ADMIN",
                datetime.datetime.now(),
                "ADMIN",
                datetime.datetime.now()
                )

        try:
            # Execute the insert query with the provided data
            self.db_helper.connect()
            insert_query = self.query_helper(INSERT_QUERY)
            self.db_helper.execute_query(insert_query, data)
            print("USERS ROLE record inserted successfully.")
        except Exception as e:
            print(f"An error occurred: {e}")
            raise Exception(e)
        finally:
            # Ensure the database connection is closed
            self.db_helper.close_connection()

        INSERT_QUERY=""" 
        INSERT INTO USERS_LOCATION
        (
        EMAIL_ADDRESS,
        LOCATION_NAME,
        CREATED_BY,
        CREATED_AT,
        UPDATED_BY,
        UPDATED_AT
        )
        VALUES (%s,%s,%s,%s,%s,%s)
        """

        

        try:
            for location in locations:

                if(len(location.strip()) == 0):
                    continue

                data = (
                        email_address,
                        location.strip(),
                        "ADMIN",
                        datetime.datetime.now(),
                        "ADMIN",
                        datetime.datetime.now()
                      )
                # Execute the insert query with the provided data
                self.db_helper.connect()
                insert_query = self.query_helper(INSERT_QUERY)
                self.db_helper.execute_query(insert_query, data)
                print("USERS LOCATION record inserted successfully.")
        except Exception as e:
            print(f"An error occurred: {e}")
            raise Exception(e)
        finally:
            # Ensure the database connection is closed
            self.db_helper.close_connection()

        return("SUCCESS")
    
    def get_location_for_user(self,email_address):
        SQL_QUERY = """ 

        SELECT LOCATION_NAME
        FROM USERS_LOCATION
        WHERE EMAIL_ADDRESS = %s

        """

        try:
            # Execute the insert query with the provided data
            self.db_helper.connect()
            sql_query = self.query_helper(SQL_QUERY)
            records = self.db_helper.fetch_all(sql_query,[email_address])
            print("USERS ROLE record fetched successfully.")
        except Exception as e:
            print(f"An error occurred: {e}")
            raise Exception(e)
        finally:
            # Ensure the database connection is closed
            self.db_helper.close_connection()

            return(records)
        
    def create_token(self,email_address):
        """
        Create a secure token for password reset.

        Args:
            user (User): The user object containing user information.

        Returns:
            str: A token that can be used to reset the password.
        """
        return self.serializer.dumps(email_address, salt=self.salt)
    
    def verify_reset_token(self,token: str): 
        try:
            email = self.serializer.loads(token, salt=self.salt, max_age=300)  # Token valid for 300 seconds
            return email
        except Exception as e:
            print(f"Token verification failed: {e}")
            return None

    def forgot_password(self,email_address):

        URL = CONFIGS.BASE_UI_URL + "reset-password"

        result = self.check_valid_user_with_email_address(email_address)

        if result is None:
            return({"message":"INVALID_EMAIL_ADDRESS"})

        token = self.create_token(email_address)
        
        # Append the token to the URL
        URL_with_token = f"{URL}?token={token}"

        # Email configuration
        smtp_server = CONFIGS.SMTP_SERVER
        smtp_port = CONFIGS.SMTP_port
        username = CONFIGS.SENDER_USERNAME  
        password = CONFIGS.SENDER_PASSWORD  

        # Email content
        sender_email = username
        recipient_email = email_address  # Replace with recipient's email
        subject = 'Welcome to the Buzzing Community!'
        body = create_body(URL_with_token)
        # Continue with sending the email as before...

        # Create the email message
        msg = MIMEMultipart('alternative')
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))  # Attach HTML content

        try:
            # Connect to the SMTP server and send the email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()  # Upgrade the connection to secure
            server.login(username, password)  # Login to your account
            server.send_message(msg)  # Send the email
            print('Email sent successfully!')
        except Exception as e:
            print(f'Failed to send email: {e}')
        finally:
            server.quit()  # Close the connection
        
        return({"message":"SUCCESS"})

    def reset_password(self,token,new_password):

        print(f"Token is {token}")
        print(f"new_password is {new_password}")
        
        email_address = self.verify_reset_token(token)

        print(f"Email is : {email_address}")
        
        










        