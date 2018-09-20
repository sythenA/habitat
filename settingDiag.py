
import os
from PyQt4 import QtGui, uic
from qgis.PyQt.QtCore import QSettings, Qt


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'settings.ui'))


class settingsDiag(FORM_CLASS, QtGui.QDialog):
    def __init__(self, parent=None):
        super(settingsDiag, self).__init__(parent)
        self.setupUi(self)

        self.settings = QSettings('ManySplendid', 'HabitatFitness')
        if self.settings.value('useBedDia') == Qt.Checked:
            self.useDiameterChkBox.setCheckState(Qt.Checked)

        self.setUnits()

    def setAttributes(self, attributeList):
        for attr in attributeList:
            self.depthAttrCombo.addItem(attr[0])
            self.xDirAttrCombo.addItem(attr[0])
            self.diameterAttrCombo.addItem(attr[0])
            self.yDirAttrCombo.addItem(attr[0])

        idx = self.depthAttrCombo.findText(
            self.settings.value('depAttr', 'Water_Depth_m'))
        if idx > -1:
            self.depthAttrCombo.setCurrentIndex(idx)

        idx = self.xDirAttrCombo.findText(
            self.settings.value('xAttr', 'Vel_X_m_p_s'))
        if idx > -1:
            self.xDirAttrCombo.setCurrentIndex(idx)

        idx = self.yDirAttrCombo.findText(
            self.settings.value('yAttr', 'Vel_Y_m_p_s'))
        if idx > -1:
            self.yDirAttrCombo.setCurrentIndex(idx)

        idx = self.diameterAttrCombo.findText(
            self.settings.value('bedDiaAttr', 'D50_mm'))
        if idx > -1:
            self.diameterAttrCombo.setCurrentIndex(idx)

    def setUnits(self):
        idx = self.depthUnit.findText(self.settings.value('depthUnit', 'm'))
        self.depthUnit.setCurrentIndex(idx)

        idx = self.xDirUnit.findText(self.settings.value('xDirUnit', 'm/s'))
        self.xDirUnit.setCurrentIndex(idx)

        idx = self.yDirUnit.findText(self.settings.value('yDirUnit', 'm/s'))
        self.yDirUnit.setCurrentIndex(idx)


class settings:
    def __init__(self):
        self.dlg = settingsDiag()
        self.settings = QSettings('ManySplendid', 'HabitatFitness')

    def run(self):
        self.dlg.show()
        result = self.dlg.exec_()

        if result == 1:
            self.settings.setValue('depAttr',
                                   self.dlg.depthAttrCombo.currentText())
            self.settings.setValue('xAttr',
                                   self.dlg.xDirAttrCombo.currentText())
            self.settings.setValue('yAttr',
                                   self.dlg.yDirAttrCombo.currentText())
            self.settings.setValue('bedDiaAttr',
                                   self.dlg.diameterAttrCombo.currentText())
            self.settings.setValue('depthUnit',
                                   self.dlg.depthUnit.currentText())
            self.settings.setValue('xDirUnit',
                                   self.dlg.xDirUnit.currentText())
            self.settings.setValue('yDirUnit',
                                   self.dlg.yDirUnit.currentText())
            self.settings.setValue('useBedDia',
                                   self.dlg.useDiameterChkBox.checkState())

    def setAttribute(self, attributeList):
        self.dlg.setAttributes(attributeList)
