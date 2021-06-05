import argparse
import os

import pytesseract
from PIL import Image
from pdf2image import convert_from_path

from api.google.vision_api import GoogleVisionApis
from utils.image_utils import overlay_image_as_paragraphs
from utils.ocr_utils import get_paragraph_details_from_annotations

OVERLAY_IMAGE_PATH = os.environ['OVERLAY_IMAGE_PATH']
OVERLAY_PDF_PATH = os.environ['OVERLAY_PDF_PATH']
TEMP_FOLDER = os.environ['TEMP_FOLDER']


class TranslationOverlay:
    def __init__(self):
        self.google_api = GoogleVisionApis()

    def create_image_with_translation_overlay(self, image_path):
        # if file is pdf, then get the jpeg files
        image_list = []
        if image_path.endswith('.pdf'):
            image_list = convert_from_path(image_path, output_folder=TEMP_FOLDER, paths_only=True)

        else:
            # check image orientation
            image = Image.open(image_path)
            image_osd = pytesseract.image_to_osd(image)
            rotate = 0
            for osd in image_osd.split('\n'):
                if osd.split(':')[0].strip() == 'Rotate':
                    rotate = int(osd.split(':')[1].strip())

            if rotate != 0:
                image = image.rotate(rotate, expand=True)

                f_name = image_path.split('/')[-1]

                # update image path to save in TEMP folder
                image_path = '{}{}'.format(TEMP_FOLDER, f_name)
                image.save(image_path)

            image_list.append(image_path)

        # get the ocr from google API
        response_json_list = []
        for idx, img in enumerate(image_list):
            response = self.google_api.request_ocr([img])

            if response.status_code != 200 or response.json().get('error'):
                raise Exception(response.text)

            response_json_list.append(response.json()['responses'])

        # get the ocr json for each of the images
        overlay_file_paths = []
        for idx, response_json in enumerate(response_json_list):
            # get the paragraph bbox dict for each page
            pages_as_para = get_paragraph_details_from_annotations(response_json[0]['fullTextAnnotation'])
            f_path = image_list[idx]

            # create overlayed image from the paragraph bbox
            for key, page_para_details in pages_as_para.items():
                overlay_file_paths.append(overlay_image_as_paragraphs(f_path, page_para_details))


        # clean the temp folder
        for f in image_list:
            os.remove(f)

        if image_path.endswith('.pdf'):
            return self.save_images_as_pdf(overlay_file_paths, image_path.split('/')[-1])

        return overlay_file_paths

    def save_images_as_pdf(self, image_names, f_name):
        image_list = []

        for name in image_names[1:]:
            im = Image.open(name)
            image_list.append(im)

        main_im = Image.open(image_names[0])
        main_im.save('{}{}'.format(OVERLAY_PDF_PATH, f_name), save_all=True, append_images=image_list)

        # clean up the image file?
        for f in image_names:
            os.remove(f)

        return '{}{}'.format(OVERLAY_PDF_PATH, f_name)


if __name__ == '__main__':
    argc = argparse.ArgumentParser(description="end to end table extraction")
    argc.add_argument("-f", "--file_path", type=str, help="pass the path for translation overlay")

    argp = argc.parse_args()
    ovl = TranslationOverlay()

    image_names = ovl.create_image_with_translation_overlay(argp.file_path)
    print(image_names)
