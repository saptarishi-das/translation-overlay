import argparse
import os

from pdf2image import convert_from_path

from api.google.vision_api import GoogleVisionApis
from utils.image_utils import overlay_image_as_paragraphs
from utils.ocr_utils import get_paragraph_details_from_annotations

OVERLAY_IMAGE_PATH = os.environ['OVERLAY_IMAGE_PATH']
TEMP_FOLDER = os.environ['TEMP_FOLDER']


class TranslationOverlay:
    def __init__(self, image_path):
        self.image_path = image_path
        self.google_api = GoogleVisionApis()

    def create_image_with_translation_overlay(self):
        # if file is pdf, then get the jpeg files
        image_list = []
        if self.image_path.endswith('.pdf'):
            image_list = convert_from_path(self.image_path, output_folder=TEMP_FOLDER, paths_only=True)

        else:
            image_list.append(self.image_path)

        # get the ocr from google API
        response_json_list = []
        for idx, image_path in enumerate(image_list):
            response = self.google_api.request_ocr([image_path])

            if response.status_code != 200 or response.json().get('error'):
                raise Exception(response.text)

            response_json_list.append(response.json()['responses'])

        # get the ocr json for each of the images
        for idx, response_json in enumerate(response_json_list):
            # get the paragraph bbox dict for each page
            pages_as_para = get_paragraph_details_from_annotations(response_json['fullTextAnnotation'])
            f_path = image_list[idx]

            # create overlayed image from the paragraph bbox
            for key, page_para_details in pages_as_para.items():
                overlay_image_as_paragraphs(f_path, page_para_details)


if __name__ == '__main__':
    argc = argparse.ArgumentParser(description="end to end table extraction")
    argc.add_argument("-f", "--file_path", type=str, help="pass the path for translation overlay")

    argp = argc.parse_args()
    ovl = TranslationOverlay(argp.file_path)
    ovl.create_image_with_translation_overlay()
