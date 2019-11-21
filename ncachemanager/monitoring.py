import os
from math import ceil, sqrt
from PySide2 import QtWidgets, QtGui, QtCore
from maya import cmds
from ncachemanager.sequencereader import SequenceImageReader, ImageViewer
from ncachemanager.playblast import compile_movie
from ncachemanager.api import connect_cacheversion
from ncachemanager.ncache import list_connected_cachefiles
from ncachemanager.versioning import (
    get_log_filename, list_tmp_jpeg_under_cacheversion)

WINDOW_TITLE = "Batch cacher monitoring"


class MultiCacheMonitor(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(MultiCacheMonitor, self).__init__(parent, QtCore.Qt.Window)
        self.setWindowTitle(WINDOW_TITLE)
        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.tab_closed)
        self.job_panels = []

        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(2, 2, 2, 2)
        self.layout.addWidget(self.tab_widget)

        self.timer = QtCore.QBasicTimer()
        self.timer.start(1000, self)

    def tab_closed(self, index):
        self.tab_widget.widget(index).kill()
        self.tab_widget.removeTab(index)
        self.job_panels.remove(index)

    def add_job(self, cacheversion, process):
        job_panel = JobPanel(cacheversion, process)
        self.job_panels.append(job_panel)
        self.tab_widget.addTab(job_panel, cacheversion.name)

    def showEvent(self, *events):
        super(MultiCacheMonitor, self).showEvent(*events)
        self.timer.start(1000, self)

    def closeEvent(self, *events):
        super(MultiCacheMonitor, self).closeEvent(*events)
        self.timer.stop()
        kill_them_all = None
        for job_panel in self.job_panels:
            if not job_panel.finished:
                if kill_them_all is None:
                    kill_them_all = kill_them_all_confirmation_dialog()
                if kill_them_all is True:
                    job_panel.kill()

    def timerEvent(self, event):
        for job_panel in self.job_panels:
            job_panel.update()


class Monitor(QtWidgets.QWidget):
    def __init__(self, names, imageviewers, parent=None):
        super(Monitor, self).__init__(parent)
        self.imageviewers = []
        for name, imageviewer_master in zip(names, imageviewers):
            imageviewer = ImageViewer(name=name)
            imageviewer_master.imageChanged.connect(imageviewer.set_image)
            self.imageviewers.append(imageviewer)
        self.layout = QtWidgets.QGridLayout(self)
        row = 0
        column = 0
        column_lenght = ceil(sqrt(len(self.imageviewers)))
        for imageviewer in self.imageviewers:
            self.layout.addWidget(imageviewer, row, column)
            column += 1
            if column >= column_lenght:
                column = 0
                row += 1


class JobPanel(QtWidgets.QWidget):
    def __init__(self, cacheversion, process, parent=None):
        super(JobPanel, self).__init__(parent)
        self.finished = False
        self.process = process
        self.cacheversion = cacheversion
        self.logfile = get_log_filename(cacheversion)
        self.imagepath = []

        startframe = cacheversion.infos['start_frame']
        endframe = cacheversion.infos['end_frame']
        self.images = SequenceImageReader(range_=[startframe, endframe])
        self.log = InteractiveLog(filepath=self.logfile)
        self.kill_button = QtWidgets.QPushButton('kill')
        self.kill_button.released.connect(self._call_kill)
        self.connect_cache = QtWidgets.QPushButton('connect cache')
        self.connect_cache.released.connect(self._call_connect_cache)
        self.connect_cache.setEnabled(False)
        self.log_widget = QtWidgets.QWidget()
        self.log_layout = QtWidgets.QVBoxLayout(self.log_widget)
        self.log_layout.setContentsMargins(0, 0, 0, 0)
        self.log_layout.setSpacing(2)
        self.log_layout.addWidget(self.log)
        self.log_layout.addWidget(self.connect_cache)
        self.log_layout.addWidget(self.kill_button)

        self.splitter = QtWidgets.QSplitter()
        self.splitter.addWidget(self.images)
        self.splitter.addWidget(self.log_widget)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.splitter)

    def update(self):
        if self.log.is_log_changed() is False or self.finished is True:
            return
        self.log.update()
        jpegs = list_tmp_jpeg_under_cacheversion(self.cacheversion)
        for jpeg in jpegs:
            # often, jpeg files are listed before to be fully written or the
            # file pysically exist. This create null pixmap and the viewport
            # has dead frames. Those checks stop the update in case of issue
            # forcing the new files to be add on next update.
            if jpeg not in self.imagepath and os.path.exists(jpeg):
                pixmap = QtGui.QPixmap(jpeg)
                if pixmap.isNull():
                    break
                self.imagepath.append(jpeg)
                self.images.add_pixmap(pixmap)

        if jpegs and self.connect_cache.isEnabled() is False:
            # allow to connect a cache only if at least one frame is cached.
            self.connect_cache.setEnabled(True)

        if self.images.isfull() is True:
            self.finished = True
            self.images.finish()
            self.kill_button.setEnabled(False)

    def _call_connect_cache(self):
        startframe = self.cacheversion.infos['start_frame']
        endframe = self.cacheversion.infos['end_frame']
        connect_cacheversion(self.cacheversion)
        cachenodes = list_connected_cachefiles()
        # because that connect a cache with is currently caching from
        # an external maya, that change the start frame and end frame of
        # the cache file node. That allow an interactive update of the
        # cache when each frame is cached.
        for cachenode in cachenodes:
            cmds.setAttr(cachenode + '.sourceStart', startframe)
            cmds.setAttr(cachenode + '.originalStart', startframe)
            cmds.setAttr(cachenode + '.originalEnd', endframe)
            cmds.setAttr(cachenode + '.sourceEnd', endframe)

    def _call_kill(self):
        self.kill()
        self.kill_button.setEnabled(False)

    def kill(self):
        if self.finished is True:
            return
        self.finished = True
        self.process.kill()
        self.images.kill()
        images = list_tmp_jpeg_under_cacheversion(self.cacheversion)
        # if the cache is not started yet, no images are already recorded
        if not images:
            return
        source = compile_movie(images)
        for image in images:
            os.remove(image)
        directory = self.cacheversion.directory
        destination = os.path.join(directory, os.path.basename(source))
        os.rename(source, destination)


class InteractiveLog(QtWidgets.QWidget):
    def __init__(self, parent=None, filepath=''):
        super(InteractiveLog, self).__init__(parent)
        self.logsize = None
        self.document = QtGui.QTextDocument()
        self.text = QtWidgets.QTextEdit()
        self.text.setReadOnly(True)
        self.text.setDocument(self.document)
        self.filepath = filepath
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.text)

    def is_log_changed(self):
        # This is an otpimization. To check if the logfile changed, that
        # compare the logfile size stored durung last update called.
        if not os.path.exists(self.filepath):
            return False
        logsize = os.path.getsize(self.filepath)
        if logsize == self.logsize:
            return False
        self.logsize = logsize
        return True

    def update(self):
        with open(self.filepath, "r") as f:
            content = f.read()
            self.document.setPlainText(content)
        scrollbar = self.text.verticalScrollBar()
        scrollbar.setSliderPosition(scrollbar.maximum())
        return True


def kill_them_all_confirmation_dialog():
    message = (
        "Some caching processes still running, do you want to kill them all ?")
    buttons = QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
    result = QtWidgets.QMessageBox.question(
        None,
        'Cache running',
        message,
        buttons,
        QtWidgets.QMessageBox.Yes)
    return result == QtWidgets.QMessageBox.Yes
