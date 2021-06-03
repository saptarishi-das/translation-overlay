# Purpose
This is a simple weekend project. The aim was to read text from an image, translate it to English and show the translated text back on the image as an overlay. This works with pdf as well

### Pre-requisites
You will need a Google API key to use this. Google API key is not free :(

### Stuff Used
1. Google API for ocr and Translation
2. Python

### Setting up
1. Clone the project and install the requirements.txt file. 
    ```
    pip install -r requirements.txt
    ```

2. Setup env variables:
    **Variable** | **Value**
    ---------|--------
    OVERLAY_IMAGE_PATH | output/image_with_overlay/
    TEMP_FOLDER | temp/
    OVERLAY_PDF_PATH | output/pdf_with_overlay/
    GOOGLE_API_KEY | **YOUR API KEY**

3. You can run the code using the emulator.py file. To do this you will need an `input` folder contianing the images / pdf to be translated and overlayed 
  
