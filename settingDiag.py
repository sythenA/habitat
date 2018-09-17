
import os
from PyQt4 import QtGui, uic
from qgis.PyQt.QtCore import QSettings


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'settings.ui'))


class settingsDiag(FORM_CLASS, QtGui.QDialog):
    def __init__(self, parent=None):
        super(settingsDiag, self).__init__(parent)
        self.setupUi(self)

        self.settings = QSettings('ManySplendid', 'HabitatFitness')

        self.setUnits()
        self.depthAttrCombo.currentIndexChanged.connect(self.depthAttrChanged)
        self.xDirAttrCombo.currentIndexChanged.connect(self.xAttrChanged)
        self.yDirAttrCombo.currentIndexChanged.connect(self.yAttrChanged)

        self.depthUnit.currentIndexChanged.connect(self.depthUnitUpdate)
        self.xDirUnit.currentIndexChanged.connect(self.xUnitUpdate)
        self.yDirUnit.currentIndexChanged.connect(self.yUnitUpdate)

    def setAttributes(self, attributeList):
        for attr in attributeList:
            self.depthAttrCombo.addItem(attr)
            self.xDirAttrCombo.addItem(attr)
            self.yDirAttrCombo.addItem(attr)

        idx = self.depthAttrCombo.findText(self.settings.value('depAttr'))
        if idx > -1:
            self.depthAttrCombo.setCurrentIndex(idx)

        idx = self.xDirAttrCombo.findText(self.settings.value('xAttr'))
        if idx > -1:
            self.xDirAttrCombo.setCurrentIndex(idx)

        idx = self.yDirAttrCombo.findText(self.settings.value('yAttr'))
        if idx > -1:
            self.yDirAttrCombo.setCurrentIndex(idx)

    def setUnits(self):
        idx = self.depthUnit.findText(self.settings.value('depthUnit', 'm'))
        self.depthUnit.setCurrentIndex(idx)

        idx = self.xDirUnit.findText(self.settings.value('xDirUnit', 'm/s'))
        self.xDirUnit.setCurrentIndex(idx)

        idx = self.yDirUnit.findText(self.settings.value('yDirUnit', 'm/s'))
        self.yDirUnit.setCurrentIndex(idx)

    def depthAttrChanged(self, idx):
        self.settings.setValue('depAttr', self.depthAttrCombo.currentText())

    def xAttrChanged(self, idx):
        self.settings.setValue('xAttr', self.xDirAttrCombo.currentText())

    def yAttrChanged(self, idx):
        self.settings.setValue('yAttr', self.yDirAttrCombo.currentText())

    def depthUnitUpdate(self, idx):
        self.settings.setValue('depthUnit', self.depthUnit.cuurentText())

    def xUnitUpdate(self, idx):
        self.settings.setValue('xDirUnit', self.xDirUnit.cuurentText())

    def yUnitUpdate(self, idx):
        self.settings.setValue('yDirUnit', self.yDirUnit.cuurentText())


class settings:
    def __init__(self):
        self.dlg = settingsDiag()

    def run(self):
        self.dlg.show()
        self.dlg.exec_()
