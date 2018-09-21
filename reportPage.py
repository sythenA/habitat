
import os
from PyQt4 import QtGui, uic
from qgis.PyQt.QtGui import QTextBrowser, QWidget, QVBoxLayout
from qgis.PyQt.QtCore import QSettings
from toUnicode import toUnicode
from habitatTEC import TECfile
from msg import MSG


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'reportPage.ui'))


class habitatReport(FORM_CLASS, QtGui.QDialog):
    def __init__(self, iface, TECs, specieItems, parent=None):
        super(habitatReport, self).__init__(parent)
        self.setupUi(self)

        self.settings = QSettings('ManySplendid', 'HabitatFitness')
        self.iface = iface

        self.tecItemList.currentItemChanged.connect(self.showTECResult)
        self.TECs = self.copyTECs(TECs)

        self.species = specieItems
        self.genCalculation()
        self.tecItemList.setCurrentRow(0)

    def copyTECs(self, TECs):
        newTECs = list()
        for tec in TECs:
            newTEC = TECfile(None, 0, tec.filePath, self.iface)
            self.tecItemList.addItem(newTEC)
            newTECs.append(newTEC)

        return newTECs

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
                self.iface.messageBar().pushMessage(str(WUAsimple))
            self.tecItemList.addItem(tecFile)

    def showTECResult(self, tec):
        self.reportTab.clear()

        browser0 = QTextBrowser()
        browser0.append('\n')
        browser0.append(toUnicode(MSG['msg18']) + u' : ' +
                        '%10.3f' % tec.totalArea + '\n')
        browser0.append(toUnicode(MSG['msg19']) + u' : ' +
                        '%10.3f' % tec.glideRatio)
        browser0.append(toUnicode(MSG['msg20']) + u' : ' +
                        '%10.3f' % tec.riffleRatio)
        browser0.append(toUnicode(MSG['msg21']) + u' : ' +
                        '%10.3f' % tec.poolRatio)
        browser0.append(toUnicode(MSG['msg21']) + u' : ' +
                        '%10.3f' % tec.runRatio)
        browser0.append('\n')
        browser0.append(toUnicode(MSG['msg23']) + u' : ' +
                        '%10.3f' % tec.divIndex)
        vLayout0 = QVBoxLayout()
        vLayout0.addWidget(browser0)
        newWidget0 = QWidget()
        newWidget0.setLayout(vLayout0)
        self.reportTab.addTab(newWidget0, toUnicode(MSG['msg17']))

        for i in range(0, len(tec.specieWUA)):
            name = tec.specieWUA[i]['name']

            browser = QTextBrowser()
            vLayout = QVBoxLayout()
            vLayout.addWidget(browser)

            browser.append('\n')
            browser.append(toUnicode(MSG['msg13']))
            browser.append(
                toUnicode(MSG['msg14']) + ' ' +
                unicode(tec.specieWUA[i]['WUAsimple']) + '\n')
            browser.append(
                toUnicode(MSG['msg15']) + ' ' +
                unicode(tec.specieWUA[i]['WUAarith']) + '\n')
            browser.append(
                toUnicode(MSG['msg16']) + ' ' +
                unicode(tec.specieWUA[i]['WUAharmonic']) + '\n')

            newWidget = QWidget()
            newWidget.setLayout(vLayout)
            self.reportTab.addTab(newWidget, name)

    def run(self):
        self.show()
        result = self.exec_()
        if result:
            pass
