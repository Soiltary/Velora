import ctypes
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import sys
import tempfile
import time
import unittest
from pathlib import Path
from ctypes.wintypes import MSG
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from PIL import Image
from PySide6.QtCore import QMimeData, QPoint, QPointF, QSettings, QUrl, Qt
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import QApplication
from velora.hotkeys import GlobalHotkeys, parse_hotkey
from velora.app import Main

APP=QApplication.instance() or QApplication([])


class API:
    def __init__(self):
        self.registered={}
        self.fail=False
    def RegisterHotKey(self,window,id,mods,vk):
        if self.fail:return 0
        self.registered[id]=(mods,vk)
        return 1
    def UnregisterHotKey(self,window,id):
        self.registered.pop(id,None)
        return 1


class ShortcutTests(unittest.TestCase):
    def test_parse_and_reserved_shortcuts(self):
        self.assertEqual(parse_hotkey('Ctrl+Space'),(0x4002,0x20))
        self.assertEqual(parse_hotkey('Alt+Q'),(0x4001,ord('Q')))
        for invalid in ['Space','Ctrl+Shift+Space','Meta+Q','Ctrl+Left','Ctrl+Q, Ctrl+W','']:
            with self.assertRaises(ValueError,msg=invalid):parse_hotkey(invalid)

    def test_replacement_conflict_keeps_old_registration(self):
        api=API()
        keys=GlobalHotkeys(APP,lambda:None,api)
        try:
            keys.set_shortcut('Ctrl+Space')
            old=keys.active_id
            api.fail=True
            with self.assertRaises(RuntimeError):keys.set_shortcut('Alt+Q')
            self.assertEqual(keys.active_id,old)
            self.assertIn(old,api.registered)
            api.fail=False
            keys.set_shortcut('Alt+Q')
            self.assertNotIn(old,api.registered)
            self.assertEqual(len(api.registered),1)
        finally:keys.close()
        self.assertEqual(api.registered,{})

    def test_native_message_dispatch(self):
        api=API()
        calls=[]
        keys=GlobalHotkeys(APP,lambda:calls.append(True),api)
        try:
            keys.set_shortcut('Ctrl+Space')
            msg=MSG()
            msg.message=0x0312
            msg.wParam=keys.active_id
            self.assertEqual(keys.nativeEventFilter(b'windows_dispatcher_MSG',ctypes.addressof(msg)),(True,0))
            self.assertEqual(len(calls),1)
            msg.wParam+=20
            self.assertEqual(keys.nativeEventFilter(b'windows_dispatcher_MSG',ctypes.addressof(msg)),(False,0))
        finally:keys.close()

    def test_hidden_window_open_then_drop_to_convert(self):
        QSettings('Velora','Velora').setValue('onboarding',False)
        w=Main()
        try:
            with tempfile.TemporaryDirectory() as tmp:
                p=Path(tmp)/'sample.png'
                Image.new('RGB',(50,40),'purple').save(p)
                # An old queue must never leak into a newly summoned wheel.
                w.add_paths([str(p)])
                w.destination=str(Path(tmp)/'result')
                w.hide()
                w.toggle_shortcut_wheel()
                APP.processEvents()
                self.assertTrue(w.wheel.isVisible())
                self.assertEqual(w.wheel.paths,[])
                self.assertFalse(w.isVisible())
                w._global_wheel and self.fail('Shortcut wheel should not auto-dismiss on mouse release')
                w.toggle_shortcut_wheel()
                self.assertFalse(w.wheel.isVisible())
                w.toggle_shortcut_wheel()
                mime=QMimeData()
                mime.setUrls([QUrl.fromLocalFile(str(p))])
                enter=QDragEnterEvent(QPoint(380,230),Qt.CopyAction|Qt.MoveAction,mime,Qt.LeftButton,Qt.ShiftModifier)
                APP.sendEvent(w.wheel,enter)
                self.assertTrue(enter.isAccepted())
                self.assertEqual(enter.dropAction(),Qt.CopyAction)
                self.assertEqual(w.wheel.items[2],'webp')
                drop=QDropEvent(QPointF(380,230),Qt.CopyAction|Qt.MoveAction,mime,Qt.LeftButton,Qt.ShiftModifier)
                APP.sendEvent(w.wheel,drop)
                self.assertTrue(drop.isAccepted())
                self.assertEqual(drop.dropAction(),Qt.CopyAction)
                deadline=time.monotonic()+15
                while w.busy() and time.monotonic()<deadline:
                    APP.processEvents()
                    time.sleep(.01)
                APP.processEvents()
                self.assertEqual(len(w.outputs),1)
                self.assertFalse(w.failures)
                self.assertTrue(p.exists())
                self.assertTrue((Path(tmp)/'result/sample.webp').exists())
        finally:
            w.quitting=True
            w.hotkeys.close()
            w.wheel.hide()
            w.close()


if __name__=='__main__':unittest.main()
