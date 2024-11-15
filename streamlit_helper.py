import streamlit as st
from model import ESRGAN_Wrapper
from PIL import Image
import io

# Shared variables
ESRGAN_trained_small = ESRGAN_Wrapper("models/small.pth")
ESRGAN_trained_large = ESRGAN_Wrapper("models/large.pth")

def init():
    # Set page to wide layout
    # st.set_page_config(layout="wide")
    # Title
    st.title("AAI3001 Large Project")
    
def imageUpload():
    st.header("File Upload")
    uploadedFile = st.file_uploader("The image you would like to upscale", type=["jpg", "jpeg", "png"])
    if uploadedFile is not None:
        img = Image.open(uploadedFile)
        # Center the image using columns
        _, col, _ = st.columns(3)
        with col:
            st.image(img, width=500)
    
    return uploadedFile

def createImgDownload(img, filename="img"):
    # Convert the PIL image to a BytesIO object for downloading as PNG
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    # Create a download button
    st.download_button(
        label="Download Image",
        data=buffer,
        file_name=f"{filename}.png",
        mime="image/png"
    )

def useModels(uploadedFile):
    # Create two columns
    col1, col2 = st.columns([1, 1])
    
    # Add content to the first column
    with col1:
        st.header("Small Model")
        st.write("A model trained on 128x128 images.")
        
        if uploadedFile is not None and st.button("Run Small Model"):
            generated_img = ESRGAN_trained_small.generate_image(uploadedFile)
            st.image(generated_img, caption="Upscaled Image")
            createImgDownload(generated_img, "output_small")

    # Add content to the second column
    with col2:
        st.header("Large Model")
        st.write("A model trained on 256x256 images.")
        
        if uploadedFile is not None and st.button("Run Large Model"):
            generated_img = ESRGAN_trained_large.generate_image(uploadedFile)
            st.image(generated_img, caption="Upscaled Image")
            createImgDownload(generated_img, "output_large")
        
    
    
    