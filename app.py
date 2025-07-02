# app/main.py

from fastapi import FastAPI, HTTPException, UploadFile, File,Form,Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import pandas as pd
from  db.sqlite.sqlitehelper import SQLiteDatabaseHelper
from UserManager.user_manager import UserManager
from FileLogManager.file_manager import FileManager
from config.configs import CONFIGS
from azure_blob.azure_blob_helper import AzureBlobHelper
from file.upload_helper import UploadFileHelper
from api.request_response_model import *
import time

from InferenceManager.image_classifier import ImageClassifier

db =SQLiteDatabaseHelper("bees.db")
os.makedirs(CONFIGS.PREDICTIONS_DIR,exist_ok=True)



app = FastAPI()
# app.mount("/files", StaticFiles(directory=CONFIGS.PREDICTIONS_DIR), name="files")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import cv2





@app.post("/api/check-valid-user")
async def check_valid_user(request:UserRequest):
    try:
        user_manager = UserManager()
        result = user_manager.check_valid_user(request.email_address,
                                               request.password)
        return(result)
        
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/api/get-uploaded-files-list")
async def get_uploaded_files_list(request:EmailRequest):
    try:
        file_manager = FileManager()
        result = file_manager.select_file_log(request.email_address)
        return(result)
        
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/api/search-results-files")
async def search_result_files(request:SearchRequest):
    try:
        print(request.model_dump())
        
        file_manager = FileManager()
        result = file_manager.select_file_log_by_created_date(request.start_date,
                                              request.end_date,
                                              request.file_description,
                                              request.location)
        return(result)
        
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/register-user")
async def register_user(request:RegistrationRequest):
    try:
        print(request.model_dump())
        user_manager = UserManager()

        result = user_manager.register_user(
            request.name, request.email,
            request.password,request.confirmPassword,
            request.locations
        )

        return ({"message": result })        
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/api/get-locations-user")
async def get_location_user(request:EmailRequest):
    try:
        print(request.model_dump())
        user_manager = UserManager()

        records = user_manager.get_location_for_user(
            request.email_address)
        return(records)
      
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/forgot-password")
async def forgot_password(request:EmailRequest):
    try:
        print(request.model_dump())
        user_manager = UserManager()

        print(request.email_address)
        result = user_manager.forgot_password(request.email_address)

        print(result)

        return(result)
    
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/reset-password")
async def reset_password(request:ResetPasswordRequest):
    try:
        print(request.model_dump())

        user_manager = UserManager()
        user_manager.reset_password(request.token,
                                    request.new_password)
        

    
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload_docs")
async def _upload_docs(file_data: UploadFile = File(...),
                       category: str = Form(...),
                       file_description: str = Form(""),
                      ):
    
    print(f"File Description : {file_description}")
    print(f"Location : {category}")

    # Start timing
    start_time = time.time()
    
    SAVE_DIR = CONFIGS.PREDICTIONS_DIR
    upload_helper = UploadFileHelper(upload_directory=f"./{CONFIGS.UPLOAD_DIR}")
    upload_helper.upload_file(file_data)

    print(f"File Upload successful")

    # Start timing
    upload_time = time.time()
    elapsed_time01 = upload_time - start_time

    file_manager = FileManager()
    file_manager.insert_file_log(file_name = file_data.filename,
                                 file_status = "UPLOADED",
                                 annotated_file_path= None,
                                 results_file_path=None,
                                 user_name="",
                                 file_description=file_description,
                                 location= category,)

    classifier = ImageClassifier()
    predictions = classifier.get_predictions(file_data.filename,category = category)
    return {"message": "File uploaded successfully",
            "prediction": predictions,
            }

 



# Run the FastAPI application with Uvicorn server (if running this file directly)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app,
        host="0.0.0.0", 
        port=8000,
    )