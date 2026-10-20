from __future__ import annotations
import ctypes
import math
import os
import sys
import threading
from pathlib import Path
from PySide6.QtCore import Qt, QTimer, QThread, Signal, QPointF, QRectF, QSettings, QUrl
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen, QFont, QIcon, QPixmap, QDesktopServices, QCursor, QKeySequence, QShortcut, QFontDatabase
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QFrame, QProgressBar, QCheckBox, QSystemTrayIcon, QMenu, QMessageBox, QDialog, QFormLayout, QSpinBox, QDoubleSpinBox, QDialogButtonBox, QKeySequenceEdit
from . import engine
from .updates import UpdateController
from .hotkeys import GlobalHotkeys
from .i18n import tr, set_language, language, source
ROOT = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent.parent))
ACCENT = '#aa96ff'

def label(text, size=12, color='#9995ad', bold=False):
    w = QLabel(tr(text))
    w.setStyleSheet(f'color:{color}; font-size:{size}px; font-weight:{(700 if bold else 400)};')
    return w

def button(text, fn, primary=False):
    b = QPushButton(tr(text))
    b.setObjectName('primary' if primary else 'secondary')
    b.setCursor(Qt.PointingHandCursor)
    b.clicked.connect(fn)
    return b

def globe_icon():
    pix = QPixmap(32,32)
    pix.fill(Qt.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setPen(QPen(QColor('#d6c3f3'),1.8))
    painter.drawEllipse(QRectF(4,4,24,24))
    painter.drawEllipse(QRectF(12,4,8,24))
    painter.drawLine(4,16,28,16)
    painter.end()
    return QIcon(pix)


def size_text(n):
    for unit in ('B', 'KB', 'MB', 'GB'):
        if n < 1024 or unit == 'GB':
            return f'{n:.1f} {unit}'
        n /= 1024

def title(action):
    names = {'strip-metadata': 'Remove metadata', 'split-pages': 'Split PDF', 'extract-audio': 'Extract audio', 'resize': 'Resize', 'rotate': 'Rotate 90°', 'grayscale': 'Grayscale', 'compress': 'Compress', 'trim': 'Trim'}
    return tr('Word (.docx)' if action == 'docx' else names.get(action, action.upper()))

class Worker(QThread):
    item_done = Signal(int, object, str)
    progress = Signal(int, int)

    def __init__(self, paths, target, destination, options):
        super().__init__()
        self.paths, self.target = (paths, target)
        self.destination, self.options = (destination, options)
        self.cancel_event = threading.Event()

    def run(self):
        if self.target == 'merge-pdf':
            try:
                output = engine.merge_pdfs(self.paths, self.destination, self.cancel_event)
                for i in range(len(self.paths)):
                    self.item_done.emit(i, output, '')
            except Exception as e:
                for i in range(len(self.paths)):
                    self.item_done.emit(i, [], str(e))
            self.progress.emit(len(self.paths), len(self.paths))
            return
        for i, path in enumerate(self.paths):
            if self.cancel_event.is_set():
                self.item_done.emit(i, [], 'Cancelled')
            else:
                try:
                    output = engine.convert(path, self.target, self.destination, self.options, self.cancel_event)
                    self.item_done.emit(i, output, '')
                except Exception as e:
                    self.item_done.emit(i, [], str(e))
            self.progress.emit(i + 1, len(self.paths))

class DropZone(QFrame):
    dropped = Signal(list)

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setObjectName('dropzone')
        self.setMinimumHeight(182)
        layout = QVBoxLayout(self)
        layout.setSpacing(7)
        layout.addStretch()
        icon = label('+', 36, ACCENT)
        icon.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon)
        heading = label('Drop files. Change their form.', 21, '#f1eefb', True)
        heading.setAlignment(Qt.AlignCenter)
        layout.addWidget(heading)
        detail = label('Images · Video · Audio · PDF · Documents · Spreadsheets · Subtitles', 12)
        detail.setAlignment(Qt.AlignCenter)
        layout.addWidget(detail)
        layout.addStretch()

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls() and any((u.isLocalFile() for u in e.mimeData().urls())):
            e.setDropAction(Qt.CopyAction)
            e.accept()

    def dropEvent(self, e):
        paths = [u.toLocalFile() for u in e.mimeData().urls() if u.isLocalFile()]
        self.dropped.emit(paths)
        e.setDropAction(Qt.CopyAction)
        e.accept()

class Wheel(QWidget):
    chosen = Signal(list, str)

    def __init__(self, mode='convert'):
        super().__init__(None, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setAcceptDrops(True)
        self.setMouseTracking(True)
        self.resize(460, 460)
        self.paths, self.items, self.hover = ([], [], -1)
        self.mode = mode
        self.received_drag = False

    def open_at_cursor(self, paths=None, beside=False):
        self.paths = list(paths or [])
        self.items = engine.common_actions(self.paths, self.mode == 'tools')
        if self.mode == 'actions':
            self.items = ['copy-path', 'show-folder', 'zip']
        self.received_drag = False
        self.hover = -1
        pos = QCursor.pos()
        screen = QApplication.screenAt(pos) or QApplication.primaryScreen()
        rect = screen.availableGeometry()
        left = pos.x() - 230
        if beside:
            left = pos.x() + 40 if pos.x() + 500 <= rect.right() else pos.x() - 500
        self.move(max(rect.left(), min(left, rect.right() - 460)), max(rect.top(), min(pos.y() - 230, rect.bottom() - 460)))
        self.show()
        self.raise_()
        self.update()

    def index_at(self, point):
        dx, dy = (point.x() - 230, point.y() - 230)
        radius = math.hypot(dx, dy)
        if not self.items or not 87 < radius < 213:
            return -1
        angle = (math.degrees(math.atan2(dx, -dy)) + 360) % 360
        return int((angle + 180 / len(self.items)) % 360 / (360 / len(self.items)))

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(QPen(QColor('#393247'), 1))
        p.setBrush(QColor('#17141f'))
        p.drawEllipse(QRectF(12, 12, 436, 436))
        if self.items:
            n = len(self.items)
            for i, item in enumerate(self.items):
                angle = -90 + i * 360 / n
                start = 90 - i * 360 / n - 180 / n
                path = QPainterPath()
                path.arcMoveTo(QRectF(20, 20, 420, 420), start)
                path.arcTo(QRectF(20, 20, 420, 420), start, 360 / n)
                end = math.radians(start + 360 / n)
                path.lineTo(230 + 90 * math.cos(end), 230 - 90 * math.sin(end))
                path.arcTo(QRectF(140, 140, 180, 180), start + 360 / n, -360 / n)
                path.closeSubpath()
                p.setBrush(QColor('#6d55b8' if i == self.hover else '#252031'))
                p.setPen(QPen(QColor('#17141f'), 5))
                p.drawPath(path)
                rad = math.radians(angle)
                x, y = (230 + 149 * math.cos(rad), 230 + 149 * math.sin(rad))
                p.setPen(QColor('#ffffff' if i == self.hover else '#ded8ee'))
                p.setFont(QFont('Noto Sans Arabic' if language() == 'ar' else 'Noto Sans', 10, QFont.DemiBold))
                text = {'copy-path': 'Copy path', 'show-folder': 'Show folder', 'zip': 'ZIP'}.get(item, title(item))
                p.drawText(QRectF(x - 62, y - 24, 124, 48), Qt.AlignCenter | Qt.TextWordWrap, tr(text))
        p.setPen(Qt.NoPen)
        p.setBrush(QColor('#121018'))
        p.drawEllipse(QRectF(144, 144, 172, 172))
        p.setPen(QColor(ACCENT))
        p.setFont(QFont('Noto Sans', 17, QFont.Bold))
        p.drawText(QRectF(145, 185, 170, 32), Qt.AlignCenter, tr('Velora'))
        p.setPen(QColor('#9c94b0'))
        p.setFont(QFont('Noto Sans Arabic' if language() == 'ar' else 'Noto Sans', 9))
        caption = ('Drop on a format' if self.items else 'Drag files here') if self.mode == 'convert' else self.mode.title()
        p.drawText(QRectF(145, 224, 170, 38), Qt.AlignCenter | Qt.TextWordWrap, tr(caption))

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            paths = [u.toLocalFile() for u in e.mimeData().urls() if u.isLocalFile()]
            if paths:
                self.paths = paths
                self.items = engine.common_actions(paths, self.mode == 'tools') if self.mode != 'actions' else ['copy-path', 'show-folder', 'zip']
                self.received_drag = True
                self.update()
                e.setDropAction(Qt.CopyAction)
                e.accept()

    def dragMoveEvent(self, e):
        self.hover = self.index_at(e.position())
        self.update()
        e.setDropAction(Qt.CopyAction)
        e.accept()

    def dragLeaveEvent(self, e):
        self.hover = -1
        self.update()

    def dropEvent(self, e):
        index = self.index_at(e.position())
        paths = self.paths[:]
        if index >= 0:
            action = self.items[index]
            self.hide()
            self.chosen.emit(paths, action)
        else:
            self.hide()
            self.chosen.emit(paths, '')
        e.setDropAction(Qt.CopyAction)
        e.accept()

    def mouseMoveEvent(self, e):
        self.hover = self.index_at(e.position())
        self.update()

    def mousePressEvent(self, e):
        if e.button() == Qt.RightButton:
            self.hide()
            return
        i = self.index_at(e.position())
        if i >= 0 and self.paths:
            self.hide()
            self.chosen.emit(self.paths[:], self.items[i])

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.hide()

class Options(QDialog):

    def __init__(self, parent, action):
        super().__init__(parent)
        self.setWindowTitle(tr(title(action) + ' settings'))
        self.setMinimumWidth(340)
        layout = QFormLayout(self)
        self.fields = {}
        fields = {'resize': [('width', 1920, 1, 32768), ('height', 1080, 1, 32768)], 'trim': [('start', 0, 0, 864000), ('end', 30, 0, 864000)], 'compress': [('quality', 80, 1, 100)]}.get(action, [])
        for key, value, low, high in fields:
            widget = QDoubleSpinBox() if action == 'trim' else QSpinBox()
            widget.setRange(low, high)
            widget.setValue(value)
            self.fields[key] = widget
            layout.addRow(tr(key.title() + (' (seconds)' if action == 'trim' else '')), widget)
        if action == 'resize':
            layout.addRow(label('Fits within these bounds. Aspect ratio is preserved.'))
        if action == 'compress':
            layout.addRow(label('Quality applies to JPEG images. PDF uses lossless\ncleanup; video uses H.264 at CRF 28. Size may vary.'))
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        for standard, text in [(QDialogButtonBox.Ok,'OK'),(QDialogButtonBox.Cancel,'Cancel')]:
            if buttons.button(standard):
                buttons.button(standard).setText(tr(text))
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def values(self):
        return {k: w.value() for k, w in self.fields.items()}

class Main(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle(tr('Velora — Local file converter'))
        self.setWindowIcon(QIcon(str(ROOT / 'assets' / 'velora.ico')))
        self.resize(1040, 800)
        self.setMinimumSize(980, 730)
        self.settings = QSettings('Velora', 'Velora')
        set_language(self.settings.value('language', 'en'))
        self.paths, self.outputs, self.failures = ([], {}, {})
        self.worker = None
        self.destination = self.settings.value('destination', '')
        self.wheel = Wheel()
        self.wheel.chosen.connect(self.wheel_chosen)
        self._last_shift = self._last_alt = self._last_ctrl = self._last_hot = False
        self._mouse_down = False
        self._release_ticks = 0
        self._global_wheel = False
        self.quitting = False
        self.shortcut = self.settings.value('wheelShortcut', 'Ctrl+Space')
        self.hotkey_error = ''
        self.updater = UpdateController(self)
        self.create_ui()
        self.create_tray()
        self.apply_language()
        self.hotkeys = GlobalHotkeys(QApplication.instance(), self.toggle_shortcut_wheel)
        QApplication.instance().aboutToQuit.connect(self.hotkeys.close)
        if os.name == 'nt':
            try:
                self.hotkeys.set_shortcut(self.shortcut)
            except (ValueError, RuntimeError) as exc:
                self.hotkey_error = str(exc)
                self.status.setText(tr('Shortcut unavailable — open Shortcuts to choose another.'))
                QTimer.singleShot(600, self.report_hotkey_error)
        self.poll = QTimer(self)
        self.poll.timeout.connect(self.poll_keys)
        if os.name == 'nt':
            self.poll.start(40)
        QShortcut(QKeySequence('Ctrl+O'), self, activated=self.browse)
        QShortcut(QKeySequence('Escape'), self, activated=self.wheel.hide)
        QShortcut(QKeySequence('Ctrl+Return'), self, activated=self.convert)
        if self.settings.value('onboarding', True, type=bool):
            self.settings.setValue('onboarding', False)
            QTimer.singleShot(500, self.show_help)

    def create_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main = QVBoxLayout(central)
        main.setContentsMargins(32, 25, 32, 22)
        main.setSpacing(16)
        header = QHBoxLayout()
        logo = QLabel()
        pix = QPixmap(str(ROOT / 'assets' / 'velora.png'))
        logo.setPixmap(pix.scaled(44, 44, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo.setFixedSize(48, 48)
        header.addWidget(logo)
        branding = QVBoxLayout()
        branding.setSpacing(0)
        wordmark = label('Velora', 28, '#f4f0ff', True)
        wordmark.setStyleSheet('color:#f4f0ff; font-family:Noto Sans; font-size:28px; font-weight:700;')
        wordmark.setLayoutDirection(Qt.LeftToRight)
        branding.addWidget(wordmark)
        branding.addWidget(label('A new form. The same flow.', 12))
        header.addLayout(branding)
        header.addStretch()
        header.addWidget(label('●  LOCAL PROCESSING', 10, '#9ed9bb', True))
        header.addSpacing(16)
        header.addWidget(button('Shortcuts', self.shortcut_settings))
        header.addWidget(button('Help', self.show_help))
        header.addWidget(button('Support', self.show_support))
        self.language_btn = button('العربية', self.toggle_language)
        self.language_btn.setObjectName('languageToggle')
        self.language_btn.setLayoutDirection(Qt.LeftToRight)
        self.language_btn.setMinimumWidth(106)
        self.language_btn.setIcon(globe_icon())
        header.addWidget(self.language_btn)
        main.addLayout(header)
        self.drop = DropZone()
        self.drop.dropped.connect(self.add_paths)
        main.addWidget(self.drop)
        controls = QHBoxLayout()
        controls.addWidget(button('+ Add files', self.browse))
        controls.addWidget(button('+ Folder', self.browse_folder))
        controls.addWidget(button('Clear', self.clear))
        controls.addStretch()
        controls.addWidget(button('Open wheel', self.open_wheel))
        main.addLayout(controls)
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels([tr('FILE'), tr('SIZE'), tr('STATUS')])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.verticalHeader().hide()
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setMinimumHeight(140)
        self.table.cellDoubleClicked.connect(self.reveal_row)
        main.addWidget(self.table, 1)
        row = QHBoxLayout()
        self.mode = QComboBox()
        self.mode.addItems([tr('Convert'), tr('Tools')])
        self.mode.currentIndexChanged.connect(self.refresh_actions)
        self.target = QComboBox()
        self.target.setMinimumWidth(195)
        self.merge_btn = button('Merge PDFs', self.merge)
        row.addWidget(self.mode)
        row.addWidget(self.target, 1)
        row.addWidget(self.merge_btn)
        self.go = button('Convert files', self.convert, True)
        self.go.setMinimumWidth(150)
        row.addWidget(self.go)
        self.cancel_btn = button('Cancel', self.cancel)
        self.cancel_btn.hide()
        row.addWidget(self.cancel_btn)
        main.addLayout(row)
        self.conversion_note = label('',11)
        self.conversion_note.setWordWrap(True)
        main.addWidget(self.conversion_note)
        self.target.currentIndexChanged.connect(self.update_conversion_note)
        output = QHBoxLayout()
        self.out_label = label('Output: ' + (self.destination or 'Velora Output beside each original'), 11)
        self.out_label.setWordWrap(True)
        output.addWidget(self.out_label, 1)
        output.addWidget(button('Choose folder', self.choose_output))
        output.addWidget(button('Reset', self.reset_output))
        output.addWidget(button('Show output', self.open_output))
        main.addLayout(output)
        self.progress = QProgressBar()
        self.progress.setFixedHeight(5)
        self.progress.setTextVisible(False)
        self.progress.setValue(0)
        main.addWidget(self.progress)
        footer = QHBoxLayout()
        self.status = label('Ready. Original files are always preserved.', 11)
        self.status.setWordWrap(True)
        footer.addWidget(self.status, 1)
        self.background = QCheckBox('Enable drag wheel')
        self.background.setChecked(self.settings.value('wheel', True, type=bool))
        self.background.toggled.connect(lambda checked: self.settings.setValue('wheel', checked))
        if os.name != 'nt':
            self.background.setEnabled(False)
            self.background.setToolTip(tr('Desktop-wide key polling is available on Windows.'))
        self.update_btn = button('Check updates', self.updater.check)
        footer.addWidget(self.update_btn)
        footer.addWidget(self.background)
        main.addLayout(footer)
        self.refresh_actions()

    def create_tray(self):
        self.tray = QSystemTrayIcon(self.windowIcon(), self)
        self.tray.setToolTip(tr('Velora — Drag a file, tap Shift'))
        menu = QMenu()
        menu.addAction(tr('Open Velora'), self.show_main)
        menu.addAction(tr('Open wheel'), self.open_wheel)
        menu.addAction(tr('Shortcuts'), self.shortcut_settings)
        menu.addAction(tr('Support'), self.show_support)
        menu.addAction(tr('Check updates'), self.updater.check)
        menu.addSeparator()
        menu.addAction(tr('Quit'), self.quit_app)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(lambda reason: self.show_main() if reason == QSystemTrayIcon.Trigger else None)
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray.show()

    def show_main(self):
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def show_help(self):
        paragraphs = [tr('Global shortcut:') + ' ' + str(self.shortcut), tr('Press the shortcut, then drag onto the wheel. Closing the window keeps Velora in the system tray. Use Quit to stop it.'), tr('Choose PDF or DOCX files, then select the output format.'), tr('PDF to Word keeps editable text; scanned pages remain images. No OCR.'), tr('DOCX to PDF works locally without Office using a basic layout. Install LibreOffice for richer formatting.'), tr('Basic Word export: text, tables and inline images. Headers, footers, floating shapes and complex layouts may change.'), tr('PDF pages: export JPG/PNG, split, merge or extract text.'), tr('Your files stay on this device. Original files are preserved.')]
        QMessageBox.information(self, tr('Velora help'), tr('\n\n'.join(paragraphs)))

    def show_support(self):
        dialog = QDialog(self)
        dialog.setWindowTitle(tr('Support Velora'))
        dialog.setMinimumWidth(440)
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(18)
        layout.addWidget(label('Support Velora', 22, '#f4effb', True))
        copy = label('If you would like to support the creator and help keep Velora growing, use the button below.', 14)
        copy.setWordWrap(True)
        layout.addWidget(copy)
        layout.addWidget(button('Support Velora ↗', lambda: QDesktopServices.openUrl(QUrl('https://tip.dokan.sa/solitary')), True))
        layout.addWidget(label('Support is optional and appreciated.', 11))
        layout.addWidget(button('Close', dialog.accept))
        dialog.exec()

    def toggle_language(self):
        set_language('en' if language() == 'ar' else 'ar')
        self.settings.setValue('language', language())
        self.apply_language()

    def apply_language(self):
        app = QApplication.instance()
        direction = Qt.RightToLeft if language() == 'ar' else Qt.LeftToRight
        app.setLayoutDirection(direction)
        family = 'Noto Sans Arabic' if language() == 'ar' else 'Noto Sans'
        fallback = 'Noto Sans' if language() == 'ar' else 'Noto Sans Arabic'
        app.setStyleSheet(STYLE + '\nQWidget {font-family:"' + family + '","' + fallback + '";} QPushButton#languageToggle {border-radius:18px; padding:8px 14px;}')
        app_font = QFont(family, 10)
        app_font.setFamilies([family, fallback])
        app.setFont(app_font)
        for widget in app.allWidgets():
            widget.setWindowTitle(tr(widget.windowTitle()))
            if isinstance(widget, (QLabel, QPushButton, QCheckBox)) and widget is not self.language_btn:
                widget.setText(tr(widget.text()))
            if isinstance(widget, QComboBox):
                for i in range(widget.count()):
                    widget.setItemText(i, tr(widget.itemText(i)))
            if isinstance(widget, QDialogButtonBox):
                for name, text in [('Ok', 'OK'), ('Cancel', 'Cancel'), ('Save', 'Save'), ('Close', 'Close')]:
                    btn = widget.button(getattr(QDialogButtonBox, name))
                    if btn:
                        btn.setText(tr(text))
            widget.setToolTip(tr(widget.toolTip()))
        for i in range(self.table.columnCount()):
            header = self.table.horizontalHeaderItem(i)
            if header:
                header.setText(tr(header.text()))
        for row in range(self.table.rowCount()):
            for col in (1, 2):
                item = self.table.item(row, col)
                if item:
                    item.setText(tr(item.text()))
            if self.table.item(row, 0):
                self.table.item(row, 0).setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        for action in self.tray.contextMenu().actions():
            action.setText(tr(action.text()))
        self.tray.setToolTip(tr(self.tray.toolTip()))
        self.language_btn.setText(tr('English' if language() == 'ar' else 'العربية'))
        self.language_btn.setToolTip(tr('Switch to English' if language() == 'ar' else 'التبديل إلى العربية'))
        self.wheel.setLayoutDirection(Qt.LeftToRight)
        self.wheel.update()

    def browse(self):
        paths, _ = QFileDialog.getOpenFileNames(self, tr('Choose files'))
        self.add_paths(paths)

    def browse_folder(self):
        path = QFileDialog.getExistingDirectory(self, tr('Choose folder to ZIP'))
        if path:
            self.add_paths([path])

    def add_paths(self, paths):
        if self.busy():
            self.status.setText(tr('Wait for the current batch to finish before adding files.'))
            return
        for path in paths:
            p = Path(path)
            if p.exists() and str(p.resolve()) not in self.paths:
                self.paths.append(str(p.resolve()))
        self.rebuild()

    def rebuild(self):
        self.table.setRowCount(len(self.paths))
        for i, path in enumerate(self.paths):
            p = Path(path)
            values = [p.name, 'Folder' if p.is_dir() else size_text(p.stat().st_size) if p.exists() else 'Missing', 'Ready']
            for j, value in enumerate(values):
                item = QTableWidgetItem(tr(value) if j else value)
                item.setToolTip(tr(str(p)))
                self.table.setItem(i, j, item)
            self.table.setRowHeight(i, 42)
        self.outputs.clear()
        self.failures.clear()
        self.refresh_actions()
        self.status.setText(tr(f'{len(self.paths)} file(s) in queue. Double-click a row to reveal its output or error.'))

    def update_conversion_note(self):
        if not hasattr(self,'conversion_note'):
            return
        action = self.target.currentData()
        if action == 'docx' and self.paths and all(Path(p).suffix.lower()=='.pdf' for p in self.paths):
            text = 'PDF to Word keeps editable text; scanned pages remain images. No OCR.'
        elif action == 'pdf' and self.paths and all(Path(p).suffix.lower()=='.docx' for p in self.paths):
            text = 'DOCX to PDF works locally without Office using a basic layout. Install LibreOffice for richer formatting.'
        else:
            text = 'Your files stay on this device. Original files are preserved.'
        self.conversion_note.setText(tr(text))

    def refresh_actions(self):
        old = self.target.currentData()
        self.target.clear()
        for item in engine.common_actions(self.paths, self.mode.currentIndex() == 1):
            self.target.addItem(title(item), item)
        idx = self.target.findData(old)
        if idx >= 0:
            self.target.setCurrentIndex(idx)
        self.go.setEnabled(bool(self.paths) and self.target.count() > 0 and (not self.busy()))
        self.merge_btn.setEnabled(len(self.paths) > 1 and all((Path(p).suffix.lower() == '.pdf' for p in self.paths)) and (not self.busy()))
        self.go.setText(tr('Apply tool' if self.mode.currentIndex() else 'Convert files'))
        self.update_conversion_note()

    def clear(self):
        if not self.busy():
            self.paths.clear()
            self.rebuild()
            self.progress.setValue(0)

    def choose_output(self):
        if self.busy():
            return
        folder = QFileDialog.getExistingDirectory(self, tr('Output folder'), self.destination)
        if folder:
            self.destination = folder
            self.settings.setValue('destination', folder)
            self.out_label.setText(tr('Output: ' + folder))

    def reset_output(self):
        if not self.busy():
            self.destination = ''
            self.settings.setValue('destination', '')
            self.out_label.setText(tr('Output: Velora Output beside each original'))

    def open_output(self):
        folder = self.destination or (str(Path(self.paths[0]).parent / 'Velora Output') if self.paths else '')
        if folder and Path(folder).exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(folder))

    def reveal_row(self, row, col):
        if row in self.failures:
            QMessageBox.warning(self, tr('Conversion details'), tr(self.failures[row]))
        elif row in self.outputs and self.outputs[row]:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(Path(self.outputs[row][0]).parent)))

    def busy(self):
        return self.worker is not None and self.worker.isRunning()

    def convert(self):
        action = self.target.currentData()
        if action:
            self.start(action)

    def merge(self):
        self.start('merge-pdf')

    def start(self, action):
        if self.busy() or not self.paths:
            return
        opts = {}
        if action in {'resize', 'trim', 'compress'}:
            dialog = Options(self, action)
            if dialog.exec() != QDialog.Accepted:
                return
            opts = dialog.values()
        self.outputs.clear()
        self.failures.clear()
        for i in range(len(self.paths)):
            self.table.item(i, 2).setText(tr('Queued'))
        self.worker = Worker(self.paths[:], action, self.destination or None, opts)
        self.worker.item_done.connect(self.item_done)
        self.worker.progress.connect(lambda n, total: self.progress.setValue(int(100 * n / total)))
        self.worker.finished.connect(self.finished)
        self.go.setEnabled(False)
        self.merge_btn.setEnabled(False)
        self.mode.setEnabled(False)
        self.target.setEnabled(False)
        self.cancel_btn.show()
        self.status.setText(tr('Processing locally…'))
        self.progress.setValue(0)
        self.worker.start()

    def item_done(self, index, paths, error):
        item = self.table.item(index, 2)
        if error:
            self.failures[index] = error
            item.setText(tr('Cancelled' if error == 'Cancelled' else 'Failed — double-click for details'))
            item.setForeground(QColor('#ed9f9f'))
            item.setToolTip(tr(error))
        else:
            self.outputs[index] = paths
            item.setText(tr('Done · ' + str(len(paths)) + ' output(s)'))
            item.setForeground(QColor('#9ed9bb'))
            item.setToolTip(tr('\n'.join((str(p) for p in paths))))

    def finished(self):
        self.cancel_btn.hide()
        self.mode.setEnabled(True)
        self.target.setEnabled(True)
        self.refresh_actions()
        message = f'Finished: {len(self.outputs)} succeeded, {len(self.failures)} failed or cancelled.'
        self.status.setText(tr(message))
        if not self.isVisible() and self.tray.isVisible():
            self.tray.showMessage('Velora', message, QSystemTrayIcon.Information, 4000)
        if self.quitting:
            QApplication.quit()

    def cancel(self):
        if self.busy():
            self.worker.cancel_event.set()
            self.status.setText(tr('Cancelling… completed files are preserved.'))

    def open_wheel(self):
        if not self.busy():
            self._global_wheel = False
            self.wheel.mode = 'tools' if self.mode.currentIndex() else 'convert'
            self.wheel.open_at_cursor(self.paths)

    def toggle_shortcut_wheel(self):
        if QApplication.activeModalWidget() is not None:
            return
        if self.wheel.isVisible():
            self.wheel.hide()
            return
        if self.busy():
            if self.tray.isVisible():
                self.tray.showMessage('Velora', 'Wait for the current conversion to finish.', QSystemTrayIcon.Information, 2500)
            return
        self._global_wheel = False
        self.wheel.mode = 'convert'
        self.wheel.open_at_cursor(beside=True)

    def report_hotkey_error(self):
        if self.hotkey_error:
            QMessageBox.warning(self, tr('Shortcut unavailable'), tr(self.hotkey_error + '\n\nOpen Shortcuts to choose another combination. The file picker and drag wheel still work.'))

    def shortcut_settings(self):
        dialog = QDialog(self)
        dialog.setWindowTitle(tr('Keyboard shortcuts'))
        dialog.setMinimumWidth(450)
        form = QFormLayout(dialog)
        form.addRow(label('Open the wheel before dragging a file.', 15, '#f1eefb', True))
        edit = QKeySequenceEdit(QKeySequence(self.shortcut))
        edit.setMaximumSequenceLength(1)
        form.addRow(tr('Open / hide wheel'), edit)
        form.addRow(label('Examples: Ctrl+Space, Alt+Q, Ctrl+F8\nA combination already used by another app cannot be saved.'))
        form.addRow(label('Ctrl+Shift+Space opens Velora. Escape closes the wheel.\nShift / Alt / Ctrl during dragging keep their existing actions.'))
        error = label('', 12, '#ed9f9f')
        error.setWordWrap(True)
        form.addRow(error)
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        for standard, text in [(QDialogButtonBox.Save,'Save'),(QDialogButtonBox.Cancel,'Cancel')]:
            if buttons.button(standard):
                buttons.button(standard).setText(tr(text))
        buttons.rejected.connect(dialog.reject)

        def save():
            sequence = edit.keySequence().toString(QKeySequence.PortableText)
            try:
                self.hotkeys.set_shortcut(sequence)
            except (ValueError, RuntimeError) as exc:
                error.setText(tr(str(exc)))
                return
            self.shortcut = sequence
            self.settings.setValue('wheelShortcut', sequence)
            self.hotkey_error = ''
            self.status.setText(tr('Wheel shortcut: ' + sequence + ' — works in the background.'))
            dialog.accept()
        buttons.accepted.connect(save)
        form.addRow(buttons)
        dialog.exec()

    def wheel_chosen(self, paths, action):
        if self.busy():
            self.show_main()
            self.status.setText(tr('Current batch is still running. Drop these files again when it finishes.'))
            return
        if action == 'copy-path':
            QApplication.clipboard().setText('\n'.join(paths))
            return
        if action == 'show-folder':
            if paths:
                QDesktopServices.openUrl(QUrl.fromLocalFile(str(Path(paths[0]).parent)))
            return
        self.paths = []
        self.add_paths(paths)
        if action:
            self.start(action)
        else:
            self.show_main()

    def poll_keys(self):
        user32 = ctypes.windll.user32
        down = lambda key: bool(user32.GetAsyncKeyState(key) & 32768)
        shift, alt, ctrl, mouse, esc = [down(k) for k in (16, 18, 17, 1, 27)]
        hot = ctrl and shift and down(32)
        if hot and (not self._last_hot):
            self.show_main()
        if esc:
            self.wheel.hide()
        if self.background.isChecked() and mouse and self._mouse_down and (not self.busy()) and (not hot) and (not self.wheel.isVisible() or self._global_wheel):
            mode = 'convert' if shift and (not self._last_shift) else 'tools' if alt and (not self._last_alt) else 'actions' if ctrl and (not self._last_ctrl) else None
            if mode:
                self.wheel.mode = mode
                self._global_wheel = True
                self.wheel.open_at_cursor()
        if self._global_wheel and self.wheel.isVisible():
            self._release_ticks = 0 if mouse else self._release_ticks + 1
            if self._release_ticks > 8:
                self.wheel.hide()
        self._mouse_down = mouse
        self._last_shift, self._last_alt, self._last_ctrl, self._last_hot = (shift, alt, ctrl, hot)

    def closeEvent(self, event):
        if self.updater.running() and not self.tray.isVisible():
            event.ignore()
            QMessageBox.information(self, tr('Updates'), tr('Wait for the update operation to finish.'))
            return
        if self.tray.isVisible() and (not self.quitting):
            self.hide()
            event.ignore()
        elif self.busy():
            self.quitting = True
            self.cancel()
            event.ignore()
        else:
            event.accept()
            QApplication.quit()

    def quit_app(self):
        if self.updater.running():
            QMessageBox.information(self, tr('Updates'), tr('Wait for the update operation to finish.'))
            return
        self.quitting = True
        self.wheel.hide()
        if self.busy():
            self.cancel()
        else:
            QApplication.quit()
STYLE = '\nQWidget {background:#111016; color:#ddd8eb; font-family:"Segoe UI"; font-size:13px;}\nQLabel {background:transparent;}\nQPushButton {border:1px solid #383143; border-radius:8px; padding:10px 15px; background:#211c2c; font-weight:600;}\nQPushButton:hover {background:#30283f; border-color:#82709f;}\nQPushButton:disabled {color:#6a6278; background:#1a1720; border-color:#26202f;}\nQPushButton#primary {background:#b5a2ff; color:#1b122e; border:0;}\nQPushButton#primary:hover {background:#c4b5ff;}\nQPushButton#primary:disabled {background:#40364f; color:#7d708f;}\nQFrame#dropzone {background:#19151f; border:1px dashed #66527f; border-radius:15px;}\nQTableWidget {background:#16131c; border:1px solid #302839; border-radius:10px; gridline-color:#28212f; selection-background-color:#3b2c53;}\nQTableWidget::item {padding:7px; border:0;}\nQHeaderView::section {background:#211b2b; color:#9f94b1; border:0; padding:10px; font-size:10px; font-weight:700;}\nQComboBox {border:1px solid #3c324a; background:#211b2a; border-radius:8px; padding:10px;}\nQComboBox QAbstractItemView {background:#211b2a; selection-background-color:#56416f;}\nQProgressBar {background:#251e2f; border:0; border-radius:2px;}\nQProgressBar::chunk {background:#b5a2ff; border-radius:2px;}\nQCheckBox {color:#a59ab6; font-size:11px;}\nQCheckBox::indicator {width:15px; height:15px; border:1px solid #6f5c89; border-radius:4px; background:#211b2a;}\nQCheckBox::indicator:checked {background:#aa96ff;}\nQSpinBox,QDoubleSpinBox {padding:8px; background:#231b30; border:1px solid #5c4973; border-radius:5px;}\nQMenu {background:#211b2b; border:1px solid #5f4e76; padding:6px;}\nQMenu::item {padding:8px 20px;}\nQMenu::item:selected {background:#49375e;}\nQToolTip {background:#322640; color:#fff; border:1px solid #69577f; padding:5px;}\n'

def main():
    app = QApplication(sys.argv)
    app.setApplicationName('Velora')
    app.setApplicationVersion('1.3.0')
    app.setOrganizationName('Velora')
    app.setStyle('Fusion')
    for font in (ROOT/'assets'/'fonts').glob('*.ttf'):
        QFontDatabase.addApplicationFont(str(font))
    app.setStyleSheet(STYLE)
    window = Main()
    paths = [p for p in sys.argv[1:] if Path(p).exists()]
    if paths:
        window.add_paths(paths)
    window.show()
    return app.exec()
