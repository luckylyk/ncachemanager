from PySide2 import QtCore, QtWidgets
from maya import cmds
from ncachefactory.ncache import DYNAMIC_NODES
from ncachefactory.attributes import (
    FILTERED_FOR_NCACHEMANAGER, filter_invisible_nodes_for_manager)


WINDOW_TITLE = "Visible for the factory"


class FilterDialog(QtWidgets.QWidget):
    updateRequested = QtCore.Signal()

    def __init__(self, parent=None):
        super(FilterDialog, self).__init__(parent, QtCore.Qt.Tool)
        self.setWindowTitle(WINDOW_TITLE)
        self.list = QtWidgets.QListWidget()
        self.list.itemChanged.connect(self.item_changed)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.list)

    def show(self):
        super(FilterDialog, self).show()
        self.fill_list()

    def fill_list(self):
        self.list.clear()
        flags = QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled
        nodes = cmds.ls(type=DYNAMIC_NODES)
        for node in sorted(nodes):
            name = cmds.listRelatives(node, parent=True)[0]
            state = not cmds.getAttr(node + '.' + FILTERED_FOR_NCACHEMANAGER)
            checkstate = QtCore.Qt.Checked if state else QtCore.Qt.Unchecked
            item = QtWidgets.QListWidgetItem(name)
            item.setFlags(flags)
            item.setCheckState(checkstate)
            item.node = node
            self.list.addItem(item)

    def item_changed(self, item):
        state = not item.checkState() == QtCore.Qt.Checked
        cmds.setAttr(item.node + '.' + FILTERED_FOR_NCACHEMANAGER, state)
        self.updateRequested.emit()
