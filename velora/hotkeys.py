"""Windows OS-registered shortcuts, including conflict-safe preference updates."""
import ctypes
import os
from PySide6.QtCore import QAbstractNativeEventFilter, Qt
from PySide6.QtGui import QKeySequence


def parse_hotkey(sequence):
    seq = QKeySequence(sequence)
    if seq.count() != 1 or seq.isEmpty():
        raise ValueError('Choose one key combination, such as Ctrl+Space or Alt+Q.')
    chord = seq[0]
    mods = chord.keyboardModifiers()
    if not (mods & (Qt.ControlModifier | Qt.AltModifier)):
        raise ValueError('Include Ctrl or Alt so normal typing is not intercepted.')
    if mods & Qt.MetaModifier:
        raise ValueError('Use Ctrl or Alt instead of the Windows key.')
    code = int(chord.key())
    if int(Qt.Key_A) <= code <= int(Qt.Key_Z) or int(Qt.Key_0) <= code <= int(Qt.Key_9):
        vk = code
    elif code == int(Qt.Key_Space):
        vk = 0x20
    elif int(Qt.Key_F1) <= code <= int(Qt.Key_F12):
        vk = 0x70 + code - int(Qt.Key_F1)
    else:
        raise ValueError('Use Space, a letter, a number, or F1–F12 with Ctrl or Alt.')
    flags = (2 if mods & Qt.ControlModifier else 0) | (1 if mods & Qt.AltModifier else 0) | (4 if mods & Qt.ShiftModifier else 0)
    if flags == 6 and vk == 0x20:
        raise ValueError('Ctrl+Shift+Space is reserved for the main window.')
    return flags | 0x4000, vk  # MOD_NOREPEAT


class GlobalHotkeys(QAbstractNativeEventFilter):
    def __init__(self, application, callback, api=None):
        super().__init__()
        self.app = application
        self.callback = callback
        self.api = api if api is not None else (ctypes.windll.user32 if os.name == 'nt' else None)
        self.active_id = None
        self.sequence = None
        self.next_id = 0x5600
        if self.api is not None:
            self.app.installNativeEventFilter(self)

    def set_shortcut(self, sequence):
        flags, vk = parse_hotkey(sequence)
        normalized = QKeySequence(sequence).toString(QKeySequence.PortableText)
        if self.api is None:
            raise RuntimeError('Global shortcuts require Windows.')
        if normalized == self.sequence and self.active_id is not None:
            return
        # Register the replacement before releasing the working shortcut.
        candidate = self.next_id
        self.next_id = 0x5600 if self.next_id >= 0x5FFF else self.next_id + 1
        if not self.api.RegisterHotKey(None, candidate, flags, vk):
            raise RuntimeError(f'{normalized} is already in use or reserved by Windows. Choose another shortcut.')
        if self.active_id is not None:
            self.api.UnregisterHotKey(None, self.active_id)
        self.active_id, self.sequence = candidate, normalized

    def nativeEventFilter(self, event_type, message):
        if self.api is not None:
            from ctypes.wintypes import MSG
            msg = MSG.from_address(int(message))
            if msg.message == 0x0312 and msg.wParam == self.active_id:
                self.callback()
                return True, 0
        return False, 0

    def close(self):
        if self.api is not None:
            if self.active_id is not None:
                self.api.UnregisterHotKey(None, self.active_id)
                self.active_id = None
            self.app.removeNativeEventFilter(self)
