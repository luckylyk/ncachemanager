
import datetime
from PySide2 import QtWidgets, QtCore
from ncachemanager.versioning import filter_cachversions_containing_nodes
from ncachemanager.manager import (
    filter_connected_cacheversions, connect_cacheversion, apply_settings)
from ncachemanager.qtutils import get_icon
from ncachemanager.attributes import set_pervertex_maps


class WorkspaceCacheversionsExplorer(QtWidgets.QWidget):
    cacheApplied = QtCore.Signal()

    def __init__(self, parent=None):
        super(WorkspaceCacheversionsExplorer, self).__init__(parent)
        self.setFixedHeight(350)
        self.cacheversion = None
        self.nodes = None

        minpolicy = QtWidgets.QSizePolicy()
        minpolicy.setHorizontalPolicy(QtWidgets.QSizePolicy.Minimum)
        maxpolicy = QtWidgets.QSizePolicy()
        maxpolicy.setHorizontalPolicy(QtWidgets.QSizePolicy.Expanding)
        self.version_label = QtWidgets.QLabel("Version: ")
        self.version_label.setSizePolicy(minpolicy)
        self.version_selector_model = CacheversionsListModel()
        self.version_selector = QtWidgets.QComboBox()
        self.version_selector.setSizePolicy(maxpolicy)
        self.version_selector.setModel(self.version_selector_model)
        self.version_selector.currentIndexChanged.connect(self._call_index_changed)
        self.version_toolbal = CacheversionToolbar()
        self.version_toolbal.setSizePolicy(minpolicy)
        self.version_layout = QtWidgets.QHBoxLayout()
        self.version_layout.setContentsMargins(0, 0, 0, 0)
        self.version_layout.addWidget(self.version_label)
        self.version_layout.addWidget(self.version_selector)
        self.version_layout.addWidget(self.version_toolbal)

        self.groupbox_infos = QtWidgets.QGroupBox()
        self.cacheversion_infos = CacheversionInfosWidget()
        self.layout_cacheversion = QtWidgets.QVBoxLayout(self.groupbox_infos)
        self.layout_cacheversion.setContentsMargins(0, 0, 0, 0)
        self.layout_cacheversion.addWidget(self.cacheversion_infos)

        self.connect_cache = QtWidgets.QPushButton("connect cache")
        self.connect_cache.released.connect(self._call_connect_cache)
        self.blend_cache = QtWidgets.QPushButton("blend cache")
        self.blend_cache.released.connect(self._call_blend_cache)
        self.connect_layout = QtWidgets.QHBoxLayout()
        self.connect_layout.setContentsMargins(0, 0, 0, 0)
        self.connect_layout.addWidget(self.connect_cache)
        self.connect_layout.addWidget(self.blend_cache)

        self.connect_input = QtWidgets.QPushButton("connect to input")
        self.connect_rest = QtWidgets.QPushButton("connect to restShape")
        self.connect_layout2 = QtWidgets.QHBoxLayout()
        self.connect_layout2.setContentsMargins(0, 0, 0, 0)
        self.connect_layout2.addWidget(self.connect_input)
        self.connect_layout2.addWidget(self.connect_rest)

        self.apply_settings = QtWidgets.QPushButton("apply settings")
        self.apply_settings.released.connect(self._call_apply_settings)
        self.blend_attributes = QtWidgets.QPushButton("%")
        self.blend_attributes.setFixedWidth(25)
        self.apply_maps = QtWidgets.QPushButton("apply maps")
        self.apply_maps.released.connect(self._call_apply_maps)
        self.attributes_layout = QtWidgets.QHBoxLayout()
        self.attributes_layout.setContentsMargins(0, 0, 0, 0)
        self.attributes_layout.setSpacing(0)
        self.attributes_layout.addWidget(self.apply_settings)
        self.attributes_layout.addSpacing(1)
        self.attributes_layout.addWidget(self.blend_attributes)
        self.attributes_layout.addSpacing(4)
        self.attributes_layout.addWidget(self.apply_maps)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setSpacing(4)
        self.layout.addLayout(self.version_layout)
        self.layout.addWidget(self.groupbox_infos)
        self.layout.addLayout(self.connect_layout)
        self.layout.addLayout(self.connect_layout2)
        self.layout.addLayout(self.attributes_layout)
        self.setEnabled(False)

    def set_nodes_and_cacheversions(self, nodes=None, cacheversions=None):
        self.nodes = nodes
        if cacheversions is None:
            self.setEnabled(False)
            self.cacheversion_infos.set_cacheversion(None)
        self.setEnabled(True)
        self.version_selector_model.set_cacheversions(
            filter_cachversions_containing_nodes(nodes, cacheversions))
        if nodes is None:
            return
        cacheversions = filter_connected_cacheversions(nodes[0], cacheversions)
        if not cacheversions:
            return
        index = self.version_selector_model.cacheversions.index(cacheversions[0])
        self.version_selector.setCurrentIndex(index)

    def _call_index_changed(self, index):
        if not self.version_selector_model.cacheversions:
            self.cacheversion = None
            self.cacheversion_infos.set_cacheversion(None)
            return
        self.cacheversion = self.version_selector_model.cacheversions[index]
        self.cacheversion_infos.set_cacheversion(self.cacheversion)

    def _call_connect_cache(self):
        connect_cacheversion(self.cacheversion, nodes=self.nodes, behavior=0)

    def _call_blend_cache(self):
        connect_cacheversion(self.cacheversion, nodes=self.nodes, behavior=2)

    def _call_apply_settings(self):
        apply_settings(self.cacheversion, self.nodes)

    def _call_apply_maps(self):
        set_pervertex_maps(self.nodes, self.cacheversion.directory)


class CacheversionsListModel(QtCore.QAbstractListModel):
    def __init__(self, parent=None):
        super(CacheversionsListModel, self).__init__(parent)
        self.cacheversions = []

    def rowCount(self, *unused_signal_args):
        return len(self.cacheversions)

    def set_cacheversions(self, cacheversions):
        self.layoutAboutToBeChanged.emit()
        self.cacheversions = cacheversions
        self.layoutChanged.emit()

    def data(self, index, role):
        if not index.isValid():
            return
        if role == QtCore.Qt.DisplayRole:
            return self.cacheversions[index.row()].infos['name']


class CacheversionInfosWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(CacheversionInfosWidget, self).__init__(parent)
        self.cacheversion = None
        self.name = QtWidgets.QLineEdit()
        self.name.setEnabled(False)
        self.name.textEdited.connect(self._call_name_changed)
        self.comment = QtWidgets.QTextEdit()
        self.comment.setFixedHeight(40)
        self.comment.setEnabled(False)
        self.comment.textChanged.connect(self._call_comment_changed)
        self.nodes_table_model = NodeInfosTableModel()
        self.nodes_table_view = NodeInfosTableView()
        self.nodes_table_view.setModel(self.nodes_table_model)

        self.form_layout = QtWidgets.QFormLayout()
        self.form_layout.setContentsMargins(0, 0, 0, 0)
        self.form_layout.addRow("name", self.name)
        self.form_layout.addRow("comment", self.comment)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addLayout(self.form_layout)
        self.layout.addWidget(self.nodes_table_view)

    def set_cacheversion(self, cacheversion):
        self.blockSignals(True)
        self.cacheversion = cacheversion
        self.nodes_table_model.set_cacheversion(cacheversion)
        self.name.setEnabled(bool(cacheversion))
        self.comment.setEnabled(bool(cacheversion))
        if cacheversion is None:
            self.name.setText("")
            self.comment.setText("")
            return
        self.name.setText(cacheversion.name)
        self.comment.setText(cacheversion.infos["comment"])
        self.nodes_table_view.update_header()
        self.blockSignals(False)

    def _call_name_changed(self, text):
        if self.cacheversion is None:
            return
        self.cacheversion.set_name(text)

    def _call_comment_changed(self, *unused_signal_args):
        if self.cacheversion is None:
            return
        self.cacheversion.set_comment(self.comment.toHtml())


class NodeInfosTableView(QtWidgets.QTableView):
    def __init__(self, parent=None):
        super(NodeInfosTableView, self).__init__(parent)
        self.configure()

    def configure(self):
        self.setShowGrid(False)
        self.setWordWrap(False)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        scrollmode = QtWidgets.QAbstractItemView.ScrollPerPixel
        self.setVerticalScrollMode(scrollmode)
        self.setHorizontalScrollMode(scrollmode)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        mode = QtWidgets.QHeaderView.ResizeToContents
        self.verticalHeader().hide()
        self.verticalHeader().setSectionResizeMode(mode)
        self.horizontalHeader().setSectionResizeMode(mode)
        self.setEditTriggers(QtWidgets.QAbstractItemView.AllEditTriggers)

    def update_header(self):
        mode = QtWidgets.QHeaderView.ResizeToContents
        self.horizontalHeader().setSectionResizeMode(mode)


class NodeInfosTableModel(QtCore.QAbstractTableModel):
    HEADERS = "Node", "Range", "Namespace", "Time spent"

    def __init__(self, parent=None):
        super(NodeInfosTableModel, self).__init__(parent)
        self.infos = None
        self.nodes = None

    def columnCount(self, _):
        return len(self.HEADERS)

    def rowCount(self, _):
        if self.nodes is None:
            return 0
        return len(self.nodes)

    def set_cacheversion(self, cacheversion):
        self.layoutAboutToBeChanged.emit()
        if cacheversion is None:
            self.infos = None
            self.nodes = None
            self.layoutChanged.emit()
            return
        self.infos = cacheversion.infos
        self.nodes = sorted([n for n in self.infos['nodes']])
        self.layoutChanged.emit()

    def sort(self, column, order):
        if column != 2:
            return
        reverse_ = order == QtCore.Qt.AscendingOrder
        self.layoutAboutToBeChanged.emit()
        self.nodes = sorted(self.nodes, reverse=reverse_)
        self.layoutChanged.emit()

    def headerData(self, section, orientation, role):
        if role != QtCore.Qt.DisplayRole:
            return
        if orientation == QtCore.Qt.Horizontal:
            return self.HEADERS[section]

    def data(self, index, role):
        if not index.isValid():
            return
        row, col = index.row(), index.column()
        node = self.nodes[row]
        if role == QtCore.Qt.DisplayRole:
            if col == 0:
                return node
            if col == 1:
                frames = self.infos['nodes'][node]['range']
                return ", ".join([str(f) for f in frames])
            if col == 2:
                return self.infos['nodes'][node]['namespace'] or 'None'
            if col == 3:
                seconds = self.infos['nodes'][node]['timespent']
                delta = datetime.timedelta(seconds=seconds)
                return str(delta)

        if role == QtCore.Qt.TextAlignmentRole:
            return QtCore.Qt.AlignCenter


class CacheversionToolbar(QtWidgets.QToolBar):

    def __init__(self, parent=None):
        super(CacheversionToolbar, self).__init__(parent)
        self.setIconSize(QtCore.QSize(15, 15))
        self.filter = QtWidgets.QAction(get_icon('filter.png'), '', self)
        self.filter.setToolTip('filter versions available for selected nodes')
        self.filter.setCheckable(True)
        self.sort = QtWidgets.QAction(get_icon('sort.png'), '', self)
        self.sort.setToolTip('sort version by')

        self.sort_menu = QtWidgets.QMenu()
        self.sort_menu.addAction('name')
        self.sort_menu.addAction('last modification')
        self.sort_menu.addAction('creation date')
        self.sort.setMenu(self.sort_menu)

        self.addAction(self.filter)
        self.addAction(self.sort)