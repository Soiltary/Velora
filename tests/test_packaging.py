import tempfile
import unittest
import zipfile
from pathlib import Path

from PIL import Image
import pillow_heif
from velora import engine


class PackagingTests(unittest.TestCase):
    def test_heif_actual_encode_decode_and_conversion(self):
        # Import alone succeeds even when the native DLL loader failed.
        self.assertTrue(pillow_heif.libheif_info()['decoders'])
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            src = root / 'heif-image.heic'
            pillow_heif.from_pillow(Image.new('RGB', (64, 48), 'purple')).save(src)
            result = engine.convert(src, 'png')[0]
            with Image.open(result) as converted:
                self.assertEqual(converted.size, (64, 48))
                converted.load()

    def test_zip_destination_is_ancestor_of_input(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            folder = root / 'Archive'
            folder.mkdir()
            (folder / 'content.txt').write_text('keep this file', encoding='utf-8')
            result = engine.convert(folder, 'zip', destination=root)[0]
            with zipfile.ZipFile(result) as archive:
                self.assertEqual(archive.read('Archive/content.txt'), b'keep this file')
