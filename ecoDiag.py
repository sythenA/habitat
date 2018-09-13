# -*- coding: big5 -*-
"""
/***************************************************************************
 habitatDialog
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

import os

from PyQt4 import QtGui, uic
from qgis.PyQt.QtGui import QTextBrowser, QVBoxLayout, QWidget, QFileDialog
from qgis.PyQt.QtCore import Qt, QSettings
from toUnicode import toUnicode
from TECfile import TECfile
from msg import MSG

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ecoUI.ui'))


class habitatDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(habitatDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.settings = QSettings('ManySplendid', 'HabitatFitness')

        self.projFolderSelectBtn.clicked.connect(self.selectProjectFolder)

        browser1 = QTextBrowser()
        vLayout = QVBoxLayout()
        vLayout.addWidget(browser1)

        newWidget = QWidget()
        newWidget.setLayout(vLayout)
        self.attributeTabs.addTab(newWidget, 'Tab1')

    def selectProjectFolder(self):
        preSet = self.settings.value('projFolder')
        projFolder = QFileDialog.getExistingDirectory(directory=preSet,
                                                      caption=MSG['msg01'])
        projFolder = toUnicode(projFolder)
        self.projFolderEdit.setText(projFolder)
