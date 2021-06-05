import json
import os
import statistics

from PIL import Image, ImageDraw, ImageFont
from googletrans import Translator

from api.google.vision_api import GoogleVisionApis
from utils.ocr_utils import get_paragraph_details_from_annotations

translator = Translator()

OVERLAY_IMAGE_PATH = os.environ['OVERLAY_IMAGE_PATH']

FONT_HEIGHT_THRESHOLD = 0.75


def get_bbox(para):
    bbox = para['bbox']
    x0, y0 = bbox['vertices'][0]['x'] if bbox['vertices'][0].get('x', None) else bbox['vertices'][3]['x'], \
             bbox['vertices'][0]['y']
    x1, y1 = bbox['vertices'][1]['x'], bbox['vertices'][1]['y']
    x2, y2 = bbox['vertices'][2]['x'], bbox['vertices'][2]['y']
    x3, y3 = bbox['vertices'][3]['x'], bbox['vertices'][3]['y']

    return x0, y0, x1, y1, x2, y2, x3, y3


def overlay_image_as_paragraphs(image_path, para_details):
    f_name = image_path.split('/')[-1].split('.')[0]
    overlay_image = '{}{}.jpeg'.format(OVERLAY_IMAGE_PATH, f_name)
    image = Image.open(image_path)
    image = image.convert('RGB')
    draw = ImageDraw.Draw(image)
    vision_api = GoogleVisionApis()

    # first draw the paragraph rectangles (to avoid overlaps)
    for para in para_details:
        x0, y0, x1, y1, x2, y2, x3, y3 = get_bbox(para)
        draw.rectangle([(x0, y0), (x2, y2)], fill='lightgrey')

    # write the text on each of the rectangles
    for para in para_details:
        x0, y0, x1, y1, x2, y2, x3, y3 = get_bbox(para)

        para_lines = para['para_lines']

        # get the mean font height
        font_height = abs(int(statistics.mean([l['line_height'] for l in para_lines])))

        # get the origin of each line
        line_origin_list = [l['origin'] for l in para_lines]

        # get the translated text for the complete para
        para_lines_list = [l['line_text'] for l in para_lines]
        response = vision_api.request_translation(para_lines_list)

        if response:
            translated_para_lines = [t['translatedText'] for t in response['translations']]
        else:
            translated_para_lines = para_lines_list

        # height allocation for each line (spacing each line of the para equally)
        h = int((int(y3) - int(y0)) / len(translated_para_lines))

        # if float(font_height) < (float(h) * FONT_HEIGHT_THRESHOLD):
        font_height = int(h * FONT_HEIGHT_THRESHOLD)

        font = ImageFont.truetype("fonts/Aaargh.ttf", font_height)

        for idx, line in enumerate(translated_para_lines):
            ox, oy = line_origin_list[idx]
            draw.text((ox, y0), line, 'purple', font=font)
            y0 = y0 + h

    image.save(overlay_image)
    return overlay_image


if __name__ == '__main__':
    ocr_json_data = json.load(open('extracted_jsons/centered_text_image.json', 'r'))
    pages_as_para = get_paragraph_details_from_annotations(ocr_json_data['fullTextAnnotation'])

    image_path = 'input/centered_text_image.png'

    for key, page_para_details in pages_as_para.items():
        overlay_image_as_paragraphs(image_path, page_para_details)
