
import os
from PyQt4 import QtGui, uic
from qgis.PyQt.QtGui import QTextBrowser, QWidget, QVBoxLayout
from qgis.PyQt.QtCore import QSettings
from toUnicode import toUnicode
from msg import MSG


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'reportPage.ui'))


class reportPageDiag(FORM_CLASS, QtGui.QDialog):
    def __init__(self, parent=None):
        super(reportPageDiag, self).__init__(parent)
        self.setupUi(self)

        self.settings = QSettings('ManySplendid', 'HabitatFitness')


class habitatReport:
    def __init__(self, TECs, specieItems):
        self.TECs = TECs
        self.species = specieItems
        self.dlg = reportPageDiag()

    def addTECs(self):
        for tecFile in self.TECs:
            self.dlg.tecItemList.addItems(tecFile)

    def genCalculation(self):
        TECs = self.TECs
        for tecFile in TECs:
            tecFile.divergence()
            for specie in self.species:
                flowFit, depFit, bedFit = tecFile.fitness(specie)
                WUAsimple, WUAarith, WUAharmonic = tecFile.fitnessByMesh(
                    flowFit, depFit, bedFit)
                tecFile.specieWUA.append({'name': specie.name,
                                          'WUAsimple': WUAsimple,
                                          'WUAarith': WUAarith,
                                          'WUAharmonic': WUAharmonic,
                                          'flowFit': flowFit,
                                          'depFit': depFit,
                                          'bedFit': bedFit})

    def showTECResult(self, tec):
        self.dlg.reportTab.clear()

        for i in range(0, len(tec.specieWUA)):
            name = tec.specieWUA[i]['name']

            browser = QTextBrowser()
            vLayout = QVBoxLayout()
            vLayout.addWidget(browser)

            browser.append('\n')
            browser.append(toUnicode(MSG['msg13']))
            browser.append(
                toUnicode(MSG['msg14']) + ' ' +
                unicode(tec.specieWUA[i]['WUAsimple']))
            browser.append(
                toUnicode(MSG['msg15']) + ' ' +
                unicode(tec.specieWUA[i]['WUAarith']))
            browser.append(
                toUnicode(MSG['msg16']) + ' ' +
                unicode(tec.specieWUA[i]['WUAharmonic']))

            newWidget = QWidget()
            newWidget.setLayout(vLayout)
            self.reportTab.addTab(newWidget, name)
