def get_paragraph_details_from_annotations(annotation):
    paragraphs = []
    # lines = []

    pages_as_para = {}
    for idx, page in enumerate(annotation['pages']):

        pages_as_para[idx] = []

        for block in page['blocks']:
            for paragraph in block['paragraphs']:
                para = ""
                line = ""
                lines = []
                for word in paragraph['words']:

                    word_bbox = word.get('boundingBox')
                    word_height = word_bbox.get('vertices')[2].get('y') - word_bbox.get('vertices')[1].get(
                        'y')  # (y2 - y1)

                    for symbol in word['symbols']:
                        line += symbol['text']
                        detected_break = symbol.get('property').get('detectedBreak', None) if symbol.get('property',
                                                                                                         None) else None
                        if detected_break:
                            if detected_break['type'] == 'SPACE':
                                line += ' '
                            if detected_break['type'] == 'EOL_SURE_SPACE':
                                line += ' '
                                # lines.append(line)
                                lines.append({
                                    'line_height': word_height,
                                    'line_text': line
                                })
                                para += '{}\n'.format(line)
                                line = ''
                            if detected_break['type'] == 'LINE_BREAK':
                                # lines.append(line)
                                lines.append({
                                    'line_height': word_height,
                                    'line_text': line
                                })
                                para += line
                                line = ''

                    # TODO - height of the line? (for font of overlay text)
                # paragraphs.append(para)

                para_details = {
                    'bbox': paragraph.get('boundingBox'),
                    'para_lines': lines
                }

                pages_as_para[idx].append(para_details)

    return pages_as_para


if __name__ == '__main__':
    from pprint import pprint
    import json

    ocr_json_data = json.load(open('tests/output/jsons/2936_3A188D61BB2B4D5198AD_22.jpeg.json', 'r'))
    pages_as_para = get_paragraph_details_from_annotations(ocr_json_data['fullTextAnnotation'])

    pprint(pages_as_para)
