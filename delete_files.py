
import sys
sys.path.append("../")
import os
from db.sqlite.sqlitehelper import SQLiteDatabaseHelper
from time import time
from config.configs import CONFIGS
from datetime import datetime, timedelta


PREDICTIONS_DIR = CONFIGS.PREDICTIONS_DIR
db_type = CONFIGS.DB_TYPE
N=24*1


db_helper = SQLiteDatabaseHelper("bees.db")


select_query = """
            SELECT 
                FILE_ID,
                ANNOTATED_FILE_PATH
            FROM 
                FILE_LOG
            WHERE 
                CREATED_AT <=  %s;

            """         
update_query = """
            UPDATE FILE_LOG
            SET ANNOTATED_FILE_PATH = NULL
            WHERE FILE_ID = %s;
            """  


def query_helper(query):

        if db_type == "DUCKDB" or db_type == "SQLITE":
            query = query.replace('%s', '?')
        
        return(query)


select_query = query_helper(select_query)
# Get current date and time
current_time = datetime.now()
# Calculate the time N hours before
time_before_n_hours = current_time - timedelta(hours=N)
db_helper.connect()
            
records = db_helper.fetch_all(select_query,
                                    [time_before_n_hours])

db_helper.close_connection()

for record in records:
    
    file_id = record[0]
    file_path = record[1]

    if (file_path):
        combined_result = "/".join(file_path.split("/")[-2:])
        predictions_file = PREDICTIONS_DIR + "/" + combined_result

        if os.path.exists(predictions_file):
            os.remove(predictions_file)  # Delete the file
            print(f"{predictions_file} has been deleted.")
        else:
            print(f"The file {predictions_file} does not exist.")
        
        db_helper.connect()
        update_query = query_helper(update_query)
        records = db_helper.execute_query(update_query,
                                            [file_id])

        db_helper.close_connection()
