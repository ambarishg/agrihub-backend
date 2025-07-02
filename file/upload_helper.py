import shutil
import os

class UploadFileHelper:

    def __init__(self,upload_directory):
        self.upload_directory = upload_directory  
        os.makedirs(self.upload_directory,exist_ok=True)

    def upload_file(self, file):
        file_location = os.path.join(self.upload_directory, file.filename)
        with open(file_location, "wb", buffering=8192) as buffer:  # 8KB buffer
            shutil.copyfileobj(file.file, buffer)
        return {"filename": file.filename}



