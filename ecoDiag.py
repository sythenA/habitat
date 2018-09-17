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
from PyQt4.QtGui import QIcon, QPixmap
from qgis.PyQt.QtGui import QTextBrowser, QVBoxLayout, QWidget, QFileDialog
from qgis.PyQt.QtCore import QSettings
from toUnicode import toUnicode
from TECfile import TECfile
from specieItem import specieItem
from readSpecieXls import readXls
from settingDiag import settings
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
        self.settingDiag = settings()

        self.projFolderSelectBtn.clicked.connect(self.selectProjectFolder)
        self.xlsSelectBtn.clicked.connect(self.selectXlsFiles)
        self.specieListWidget.currentItemChanged.connect(self.showAttribute)
        self.callSettingsBtn.clicked.connect(self.settingDiag.run)

        pixMap = QPixmap(os.path.join(os.path.dirname(__file__),
                                      'settings.svg'))
        settingIcon = QIcon(pixMap)
        self.callSettingsBtn.setIcon(settingIcon)
        self.callSettingsBtn.setIconSize(0.1*pixMap.rect().size())

    def selectProjectFolder(self):
        preSet = self.settings.value('projFolder')
        projFolder = QFileDialog.getExistingDirectory(
            directory=preSet, caption=toUnicode(MSG['msg01']))
        projFolder = toUnicode(projFolder)
        self.projFolderEdit.setText(projFolder)

    def selectXlsFiles(self):
        projFolder = toUnicode(self.projFolderEdit.text())
        xlsFiles = QFileDialog.getOpenFileNames(
            directory=projFolder, filter='*.xls; *.xlsx',
            caption=toUnicode(MSG['msg06']))
        textString = ''
        for xls in xlsFiles:
            textString = xls + ';'
            textString = textString[0: -1]
        self.xlsFilesEdit.setText(textString)
        items = list()
        itemNames = list()
        for xlsFile in xlsFiles:
            Species = readXls(xlsFile)
            for specie in Species:
                if toUnicode(specie[0][13]) not in itemNames:
                    itemNames.append(toUnicode(specie[0][13]))
                    specieListItem = specieItem(toUnicode(specie[0][13]),
                                                specie,
                                                self.specieListWidget)
                    items.append(specieListItem)
        for item in items:
            self.specieListWidget.addItem(item)

        if items:
            self.specieListWidget.setCurrentRow(0)
            item = self.specieListWidget.currentItem()
            self.showAttribute(item)

    def showAttribute(self, item):
        self.attributeTabs.clear()

        browser0 = QTextBrowser()
        vLayout = QVBoxLayout()
        vLayout.addWidget(browser0)

        browser0.append(toUnicode(item.name))
        browser0.append(toUnicode(MSG['msg08']))
        string = ''
        for name in item.cName:
            string += ('    ' + toUnicode(name) + '\n')
        browser0.append(string)
        browser0.append(toUnicode(MSG['msg09'])
                        + ' : ' + toUnicode(item.family) + '  ' +
                        item.Efamily)
        browser0.append(toUnicode(MSG['msg11']) + ' : ' +
                        toUnicode(item.BinoName))
        browser0.append(toUnicode(MSG['msg10']) + ' : ' +
                        toUnicode(item.region))
        browser0.append(toUnicode(MSG['msg12']) + ' : ' +
                        toUnicode(item.researcher))

        newWidget = QWidget()
        newWidget.setLayout(vLayout)
        self.attributeTabs.addTab(newWidget, toUnicode(MSG['msg07']))

        browser1 = QTextBrowser()
        vLayout = QVBoxLayout()
        vLayout.addWidget(browser1)

        for row in item.flowCategory:
            string = (row[0] + ' ' + item.flowUnit + ' < ' +
                      toUnicode(MSG['msg04']) +
                      ' <= ' + row[1] + ' ' + item.flowUnit +
                      ' : ' + row[2])
            browser1.append(string)

        newWidget = QWidget()
        newWidget.setLayout(vLayout)
        self.attributeTabs.addTab(newWidget, toUnicode(MSG['msg04']))

        browser2 = QTextBrowser()
        vLayout = QVBoxLayout()
        vLayout.addWidget(browser2)

        for row in item.depthCategory:
            string = (row[0] + ' ' + item.depthUnit + ' < ' +
                      toUnicode(MSG['msg03']) +
                      ' <= ' + row[1] + ' ' + item.depthUnit +
                      ' : ' + row[2])
            browser2.append(string)

        newWidget = QWidget()
        newWidget.setLayout(vLayout)
        self.attributeTabs.addTab(newWidget, toUnicode(MSG['msg03']))

        browser3 = QTextBrowser()
        vLayout = QVBoxLayout()
        vLayout.addWidget(browser3)

        for row in item.bedCategory:
            string = (row[0] + ' ' + item.bedUnit + ' < ' +
                      toUnicode(MSG['msg05']) +
                      ' <= ' + row[1] + ' ' + item.bedUnit +
                      ' : ' + row[2])
            browser3.append(string)

        newWidget = QWidget()
        newWidget.setLayout(vLayout)
        self.attributeTabs.addTab(newWidget, toUnicode(MSG['msg05']))
