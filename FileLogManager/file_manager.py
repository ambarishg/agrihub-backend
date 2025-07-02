from config.configs import CONFIGS
from db.sqlite.sqlitehelper import SQLiteDatabaseHelper
from db.mysql.mysqlhelper import MySQLHelper
import datetime
from uuid import uuid4

class FileManager:
    def __init__(self,
                 db_type = None,
                 database_file = None,
                 ):

        if db_type is None :
          self.db_type = CONFIGS.DB_TYPE
        else:
            self.db_type = db_type

        if self.db_type == "SQLITE":
            if database_file is None:
                self.database_file = CONFIGS.DATABASE_FILE
            else:
                self.database_file = database_file
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
    
    def insert_file_log(self,
                        file_name,
                        file_status,
                        annotated_file_path,
                        results_file_path,
                        user_name,
                        file_description,
                        location
                        ):
        
        self._insert_file_log(file_name,
                        file_status,
                        annotated_file_path,
                        results_file_path,
                        user_name,
                        user_name,
                        datetime.datetime.now(),
                        user_name ,
                        datetime.datetime.now(),
                        file_description,
                        location)
    
    def _insert_file_log(self,
                        file_name,
                        file_status,
                        annotated_file_path,
                        results_file_path,
                        user_name,
                        created_by,
                        created_at,
                        updated_by,
                        updated_at,
                        file_description,
                        location):
        
        INSERT_QUERY=""" 
        INSERT INTO FILE_LOG
        (
        FILE_NAME,
        FILE_STATUS,
        ANNOTATED_FILE_PATH,
        RESULTS_FILE_PATH,
        USER_NAME,
        CREATED_BY,
        CREATED_AT,
        UPDATED_BY,
        UPDATED_AT,
        FILE_DESCRIPTION,
        LOCATION,
        FILE_ID
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        file_id = str(uuid4())
        data = (
            file_name,
            file_status,
            annotated_file_path,
            results_file_path,
            user_name,
            created_by,
            created_at,
            updated_by,
            updated_at,
            file_description,
            location,
            file_id
        )

        try:
            # Execute the insert query with the provided data
            self.db_helper.connect()
            insert_query = self.query_helper(INSERT_QUERY)
            self.db_helper.execute_query(insert_query, data)
            print("FILE_LOG record inserted successfully.")
        except Exception as e:
            print(f"An error occurred: {e}")
            raise Exception(e)
        finally:
            # Ensure the database connection is closed
            self.db_helper.close_connection()

    def update_file_log(self,
                        file_name,
                        annotated_file_path,
                        results_file_path,
                        user_name,
                        file_id,
                        file_status =  "PROCESSED"):
        
        UPDATE_QUERY=""" 
        UPDATE FILE_LOG
        
        SET ANNOTATED_FILE_PATH =   %s,
            RESULTS_FILE_PATH = %s,
            UPDATED_BY = %s,
            UPDATED_AT = %s,
            FILE_STATUS = %s
        WHERE 
           file_name = %s
           AND USER_NAME =  %s
           AND file_id = %s
        """
        data = (
            
            annotated_file_path,
            results_file_path,
            user_name,
            datetime.datetime.now(),
            file_status,
            file_name,
            user_name,
            file_id
        )

        try:
            # Execute the insert query with the provided data
            self.db_helper.connect()
            UPDATE_QUERY = self.query_helper(UPDATE_QUERY)
            self.db_helper.execute_query(UPDATE_QUERY, data)
            print("FILE_LOG record updated successfully.")
        except Exception as e:
            print(f"An error occurred: {e}")
            raise Exception(e)
        finally:
            # Ensure the database connection is closed
            self.db_helper.close_connection()
   

    def select_file_log(self,email_address):
        
        select_query = """
        SELECT 
            FILE_NAME,
            FILE_STATUS,
            ANNOTATED_FILE_PATH,
            RESULTS_FILE_PATH,
            LOCATION,
            UPDATED_AT
        FROM 
            FILE_LOG
        WHERE 
            USER_NAME = %s
        ORDER BY 
            UPDATED_AT DESC;

        """
        
        select_query = self.query_helper(select_query)


        try:
            self.db_helper.connect()
            
            records = self.db_helper.fetch_all(select_query,[email_address])
            print("FILE_LOG data fetched successfully")
        except Exception as e:
            print(f"An error occurred: {e}")
            raise Exception(e)
        finally:
            # Ensure the database connection is closed
            self.db_helper.close_connection()
        
        return records
    
    def select_file_log_to_process(self):
        
        select_query = """
        SELECT 
            FILE_NAME,
            USER_NAME,
            FILE_ID,
            FILE_DESCRIPTION
        FROM 
            FILE_LOG
        WHERE 
            FILE_STATUS = %s
        ORDER BY 
            UPDATED_AT ASC;

        """
        
        select_query = self.query_helper(select_query)

        FILE_STATUS = "UPLOADED"
        try:
            self.db_helper.connect()
            
            records = self.db_helper.fetch_all(select_query,[FILE_STATUS])
            
            if(len(records) == 0):
                return None
            
            print("FILE_LOG data fetched successfully")
        except Exception as e:
            print(f"An error occurred: {e}")
            raise Exception(e)
        finally:
            # Ensure the database connection is closed
            self.db_helper.close_connection()
        
        return records[0]
    
    def select_file_log_by_created_date(self,
                                        start_date,
                                        end_date,file_description,location):
        
        file_description = file_description.strip()
        location = location.strip()

        print(f"LOCATION is {location}")

        order_by_cluase = "ORDER BY CREATED_AT DESC;"
        data = [start_date,end_date]
        print(f"DATA IS {data}")

        if(file_description == "") and (location == ""):

            select_query = """
            SELECT 
                FILE_NAME,
                FILE_STATUS,
                ANNOTATED_FILE_PATH,
                RESULTS_FILE_PATH,
                LOCATION,
                CREATED_AT,
                USER_NAME
            FROM 
                FILE_LOG
            WHERE 
                CREATED_AT >=  %s AND  CREATED_AT < %s
            ORDER BY 
                CREATED_AT DESC;

            """
            
        else:
            print("CONTROL IS IN ELSE BLOCK----------")
            select_query = """
            SELECT 
                FILE_NAME,
                FILE_STATUS,
                ANNOTATED_FILE_PATH,
                RESULTS_FILE_PATH,
                LOCATION,
                CREATED_AT,
                USER_NAME
            FROM 
                FILE_LOG
            WHERE 
                CREATED_AT >=  %s AND  CREATED_AT < %s
                """
            
            if(len(file_description) > 0 ):
                print("CONTROL IS IN file_description BLOCK----------")
                file_description_clause = """ 
                AND file_description LIKE %s 
                """
                              
                select_query = select_query + file_description_clause
                file_description = "%" + file_description + "%"
                data.append(file_description)

            if(len(location) > 0 ):
                print("CONTROL IS IN LOCATION BLOCK----------")
                location_clause = """ 
                AND location LIKE %s 
                """
                              
                select_query = select_query + location_clause
                location = "%" + location + "%"
                data.append(location)
            
            select_query = select_query + " " + order_by_cluase
        
        print(f"DATA IS {data}")
        select_query = self.query_helper(select_query)

        print(f"SELECT QUERY is {select_query}")
        print(f"file_description is {file_description}")

        try:
            self.db_helper.connect()
            
            records = self.db_helper.fetch_all(select_query,
                                               data)
            print("FILE_LOG data fetched successfully")
        except Exception as e:
            print(f"An error occurred: {e}")
            raise Exception(e)
        finally:
            # Ensure the database connection is closed
            self.db_helper.close_connection()
        
        return records
