from unittest import TestCase

from PIL import Image

from qtar.core.container import Key
from qtar.core.qtar import QtarStego


TESTING_CONTAINER_PATH = "images/Lenna.png"
TESTING_WATERMARK_PATH = "images/Garold.png"
TESTING_KEY_PATH = "test_key.qtarkey"


class TestKey(TestCase):
    def setUp(self):
        self.container = Image.open(TESTING_CONTAINER_PATH)
        self.watermark = Image.open(TESTING_WATERMARK_PATH)

    def test_save_open(self):
        embed_result = QtarStego().embed(self.container, self.watermark)
        key = embed_result.key
        key.save(TESTING_KEY_PATH)
        opened_key = Key.open(TESTING_KEY_PATH)

        self.assertAlmostEqual(opened_key.ch_scale, key.ch_scale, 3, "ch_scale")
        self.assertEqual(opened_key.offset, key.offset, "offset")
        self.assertEqual(opened_key.wm_shape, key.wm_shape, "wm_shape")

        for ch in range(len(key.chs_qt_key)):
            self.assertEqual(opened_key.chs_qt_key[ch], key.chs_qt_key[ch], "qt_key")
            # self.assertCountEqual(opened_key.chs_cf_key[ch], key.chs_cf_key[ch], "cf_key")

    def tearDown(self):
        self.container.close()
        self.watermark.close()
