import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import tempfile
import unittest
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSettings,Qt
from PySide6.QtGui import QFontDatabase
from PIL import Image
from velora.app import Main,ROOT
from velora.i18n import language
APP=QApplication.instance() or QApplication([])
for font in (ROOT/'assets/fonts').glob('*.ttf'):QFontDatabase.addApplicationFont(str(font))

class LanguageTests(unittest.TestCase):
 def test_switch_preserves_files_target_and_paths(self):
  settings=QSettings('Velora','Velora');settings.setValue('onboarding',False);settings.setValue('language','en')
  window=Main()
  try:
   with tempfile.TemporaryDirectory() as tmp:
    path=Path(tmp)/'Ready صورة.png';Image.new('RGB',(20,20),'purple').save(path)
    window.add_paths([str(path)]);window.target.setCurrentIndex(window.target.findData('jpg'));before=list(window.paths)
    window.toggle_language();APP.processEvents()
    self.assertEqual(language(),'ar');self.assertEqual(window.layoutDirection(),Qt.RightToLeft)
    self.assertEqual(window.paths,before);self.assertEqual(window.target.currentData(),'jpg')
    self.assertEqual(window.table.item(0,0).text(),path.name)
    self.assertEqual(settings.value('language'),'ar');self.assertEqual(window.language_btn.text(),'English')
    window.toggle_language();APP.processEvents();self.assertEqual(window.paths,before);self.assertEqual(window.target.currentData(),'jpg')
    self.assertEqual(window.table.horizontalHeaderItem(0).text(),'FILE')
  finally:
   settings.setValue('language','en');window.quitting=True;window.hotkeys.close();window.wheel.hide();window.close()
if __name__=='__main__':unittest.main()
