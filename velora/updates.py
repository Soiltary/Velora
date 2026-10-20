from __future__ import annotations
import os,subprocess,tempfile,shutil
from pathlib import Path
from PySide6.QtCore import QObject,QThread,QTimer,Signal
from PySide6.QtWidgets import QApplication,QMessageBox
from PySide6.QtWidgets import QSystemTrayIcon
from . import update_core
from .i18n import tr

class UpdateWorker(QThread):
    progress=Signal(int)
    def __init__(self,manifest=None):
        super().__init__();self.manifest=manifest;self.result=None;self.error=None
    def run(self):
        try:
            if self.manifest is None:self.result=update_core.check()
            else:
                work=Path(os.environ.get('LOCALAPPDATA',tempfile.gettempdir()))/'Velora'/'Updates';work.mkdir(parents=True,exist_ok=True)
                folder=Path(tempfile.mkdtemp(prefix='release-',dir=work));self.result=update_core.download(self.manifest,folder/'update.zip',self.progress.emit)
        except Exception as exc:self.error=exc

class UpdateController(QObject):
    def __init__(self,main):
        super().__init__(main);self.main=main;self.worker=None;self.manifest=None;self.archive=None
        self.timer=QTimer(self);self.timer.timeout.connect(lambda:self.check(True));
        if os.name=='nt' and os.environ.get('QT_QPA_PLATFORM')!='offscreen':
            self.timer.start(6*60*60*1000)
            QTimer.singleShot(1500,lambda:self.check(True))
    def running(self):return self.worker is not None and self.worker.isRunning()
    def check(self,quiet=False):
        if self.running() or QApplication.activeModalWidget():return
        if self.main.busy():
            if not quiet:QMessageBox.information(self.main,tr('Updates'),tr('Finish the current conversion before updating.'))
            return
        if self.archive and not quiet:self.install();return
        if self.manifest and not quiet:self.offer();return
        self.begin(None,quiet)
    def begin(self,manifest,quiet):
        self.worker=UpdateWorker(manifest);worker=self.worker;self.main.update_btn.setEnabled(False)
        self.main.update_btn.setText(tr('Checking updates...' if manifest is None else 'Downloading update...'))
        worker.progress.connect(lambda n:self.main.update_btn.setText(tr('Downloading update...')+f' {n}%'))
        worker.finished.connect(lambda:self.completed(worker,quiet));worker.start()
    def completed(self,worker,quiet):
        self.worker=None;self.main.update_btn.setEnabled(True);self.main.update_btn.setText(tr('Check updates'));worker.deleteLater()
        if worker.error:
            if not quiet:QMessageBox.warning(self.main,tr('Updates'),tr('Could not download or verify the update. Your installed version is unchanged.'))
            return
        if worker.manifest is None:
            if worker.result:
                self.manifest=worker.result;self.main.update_btn.setText(tr('Update available'))
                if quiet:self.main.tray.showMessage('Velora',tr('An update is available. Use Check updates to install it.'),QSystemTrayIcon.Information,5000)
                else:self.offer()
            elif not quiet:QMessageBox.information(self.main,tr('Updates'),tr('You have the latest version.')+'\nVelora '+update_core.VERSION)
        else:self.archive=Path(worker.result);self.install()
    def offer(self):
        if QMessageBox.question(self.main,tr('Updates'),tr('Install update now? Velora will close and reopen. Settings and personal files are kept.')+'\n\nVelora '+self.manifest['version'],QMessageBox.Yes|QMessageBox.No,QMessageBox.No)==QMessageBox.Yes:self.begin(self.manifest,False)
    def install(self):
        if self.main.busy():
            self.main.update_btn.setText(tr('Update available'));QMessageBox.information(self.main,tr('Updates'),tr('Finish the current conversion before updating.'));return
        from .app import ROOT
        script=self.archive.parent/'apply-update.ps1';shutil.copyfile(ROOT/'velora'/'apply_update.ps1',script)
        shell=Path(os.environ.get('SystemRoot',r'C:\Windows'))/'System32'/'WindowsPowerShell'/'v1.0'/'powershell.exe'
        try:
            subprocess.Popen([str(shell),'-NoLogo','-NoProfile','-ExecutionPolicy','Bypass','-File',str(script),'-Target',str(ROOT),'-Archive',str(self.archive),'-ExpectedHash',self.manifest['sha256'],'-AppProcess',str(os.getpid()),'-LauncherProcess',str(os.getppid())],creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        except OSError:
            QMessageBox.warning(self.main,tr('Updates'),tr('Could not launch the updater. Please try again.'));return
        self.main.quitting=True;self.main.wheel.hide();self.main.tray.hide();self.main.settings.sync();QApplication.quit()
