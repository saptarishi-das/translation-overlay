from overlay.translation_overlay import TranslationOverlay
from os import walk

ovl = TranslationOverlay()

_, _, f_name = next(walk('input'))
for name in f_name:
    print('processing: {}'.format(name))
    image_names = ovl.create_image_with_translation_overlay('input/{}'.format(name))
    print(image_names)