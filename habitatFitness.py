"""
/***************************************************************************
 habitat
                                 A QGIS plugin
 Measuring habitat fitness for Taiwan unique species using SRH-2D results
                              -------------------
        begin                : 2018-09-13
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Manysplendid co.
        email                : yengtinglin@manysplendid.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt
from PyQt4.QtGui import QAction, QIcon
from qgis.PyQt.QtGui import QFileDialog
# Import the code for the dialog
from ecoDiag import habitatDialog
from toUnicode import toUnicode
from msg import MSG
from habitatTEC import TECfile
from specieItem import specieItem
from reportPage import habitatReport
import os.path


class habitat:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgisInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'habitat_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Taiwan Unique Species Habitat Fitness')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'habitat')
        self.toolbar.setObjectName(u'habitat')
        self.dlg = habitatDialog()
        self.settings = QSettings('ManySplendid', 'HabitatFitness')

        self.dlg.addTecBtn.clicked.connect(self.addTECFiles)
        self.dlg.deleteTecBtn.clicked.connect(self.deleteTECFile)

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('habitat', message)

    def add_action(self,
                   icon_path,
                   text,
                   callback,
                   enabled_flag=True,
                   add_to_menu=True,
                   add_to_toolbar=True,
                   status_tip=None,
                   whats_this=None,
                   parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = os.path.join(self.plugin_dir, '0fish-01.png')
        self.add_action(
            icon_path,
            text=self.tr(u'Habitat Fitness Measurement Module'),
            callback=self.run,
            parent=self.iface.mainWindow())

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Taiwan Unique Species Habitat Fitness'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def getSpecieItems(self):
        specieItems = list()

        for i in range(0, self.dlg.specieListWidget.count()):
            if self.dlg.specieListWidget.item(i).checkState() == Qt.Checked:
                specieItems.append(self.dlg.specieListWidget.item(i))
        return specieItems

    def run(self):
        self.dlg.show()
        result = self.dlg.exec_()
        if result == 1:
            specieItems = self.getSpecieItems()
            self.settings.setValue(
                'projFolder',
                toUnicode(self.dlg.projFolderEdit.text()))
            rep = habitatReport(
                self.iface, [self.dlg.tecSelectListWidget.item(0)],
                specieItems)
            rep.run()

    def addTECFiles(self):
        filePath = QFileDialog.getOpenFileName(
            caption=toUnicode(MSG['msg02']),
            directory=self.dlg.projFolderEdit.text(),
            filter="*.dat")

        if filePath:
            fileWidget = TECfile(self.dlg.tecSelectListWidget, 0,
                                 toUnicode(filePath),
                                 self.iface)
            self.dlg.tecSelectListWidget.addItem(fileWidget)
            self.dlg.addAttributeToSettings()
        # Limit allowed TEC file to 1 TEC file only
        if self.dlg.tecSelectListWidget.count() >= 1:
            self.dlg.addTecBtn.setEnabled(False)

    def deleteTECFile(self):
        selectedTEC = self.dlg.tecSelectListWidget.currentItem()
        c_row = self.dlg.tecSelectListWidget.row(selectedTEC)
        self.dlg.tecSelectListWidget.takeItem(c_row)

        # Limit allowed TEC file to 1 TEC file only
        if self.dlg.tecSelectListWidget.count() == 0:
            self.dlg.addTecBtn.setEnabled(True)
