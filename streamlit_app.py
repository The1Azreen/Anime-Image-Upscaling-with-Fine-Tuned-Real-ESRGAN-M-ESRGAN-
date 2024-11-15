# import module
from streamlit_helper import init, imageUpload, useModels
    
if __name__ == "__main__":
    init()
    
    uploadedFile = imageUpload()
    useModels(uploadedFile)
    
    