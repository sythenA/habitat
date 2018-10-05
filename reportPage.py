
import os
from PyQt4 import QtGui, uic
from qgis.PyQt.QtGui import QTextBrowser, QWidget, QVBoxLayout, QFileDialog
from qgis.PyQt.QtGui import QMessageBox
from qgis.PyQt.QtCore import QSettings, QCoreApplication
from toUnicode import toUnicode
from habitatTEC import TECfile
import io
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
        self.resultExportBtn.clicked.connect(self.genReport)

    def copyTECs(self, TECs):
        newTECs = list()
        for tec in TECs:
            newTEC = TECfile(None, 0, tec.filePath, self.iface)
            self.tecItemList.addItem(newTEC)
            newTECs.append(newTEC)

        return newTECs

    def tr(self, message):
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('habitatReport', message)

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
            self.tecItemList.addItem(tecFile)

    def reportAsTxt(self, tec, saveFile):
        with io.open(saveFile, 'w', encoding='utf-8') as f:
            f.write(toUnicode(MSG['msg17']) + ' : ' + '\n')

            if tec.mapUnit == 'meter':
                area_factor = 1.0E-6
                area_unit = u'km^2'
            elif tec.mapUnit == 'feet':
                area_factor = 1./43560
                area_unit = u'Acre'
            else:
                area_factor = 1.0
                area_unit = ''

            f.write(toUnicode(MSG['msg18']) + u' : ' +
                    unicode('%10.3f' % (tec.totalArea*area_factor) +
                            ' ' + area_unit + '\n'))
            f.write(u'\n')
            f.write(toUnicode(MSG['msg19']) + u' : ' +
                    unicode('%10.3f' % tec.glideRatio) + u'\n')
            f.write(toUnicode(MSG['msg20']) + u' : ' +
                    unicode('%10.3f' % tec.riffleRatio) + u'\n')
            f.write(toUnicode(MSG['msg21']) + u' : ' +
                    unicode('%10.3f' % tec.poolRatio) + u'\n')
            f.write(toUnicode(MSG['msg22']) + u' : ' +
                    unicode('%10.3f' % tec.runRatio) + u'\n')
            f.write(u'\n')

            f.write(toUnicode(MSG['msg23']) + u' : ' +
                    unicode('%10.3f' % tec.divIndex) + u'\n')
            f.write(u'\n')
            f.write(u'='*40 + u'\n')

            for i in range(0, len(tec.specieWUA)):
                name = tec.specieWUA[i]['name']
                f.write(toUnicode(name) + '  ' + toUnicode(MSG['msg13']) +
                        u'\n')
                f.write(u'\n')

                f.write(toUnicode(MSG['msg14']) + ' ' +
                        unicode('%10.3f' % (tec.specieWUA[i]['WUAsimple']*area_factor)) +
                        u' ' + area_unit+ u'\n')
                f.write(toUnicode(MSG['msg24']) + ' ' +
                        unicode('%10.3f' % (tec.specieWUA[i]['WUAsimple']/tec.totalArea))
                        + u'\n')
                f.write(u'\n')
                f.write(toUnicode(MSG['msg15']) + ' ' +
                        unicode('%10.3f' % (tec.specieWUA[i]['WUAarith']*area_factor)) +
                        ' ' + area_unit+ u'\n')
                f.write(toUnicode(MSG['msg24']) + ' ' +
                        unicode('%10.3f' % (tec.specieWUA[i]['WUAarith']/tec.totalArea)) +
                        u'\n')
                f.write(u'\n')
                f.write(toUnicode(MSG['msg16']) + ' ' +
                        unicode('%10.3f' % (tec.specieWUA[i]['WUAharmonic']*area_factor)) +
                        u' ' + area_unit + u'\n')
                f.write(u'\n')
                f.write(toUnicode(MSG['msg24']) + ' ' +
                        unicode('%10.3f' % (tec.specieWUA[i]['WUAharmonic']/tec.totalArea)) +
                        u'\n')
                f.write(u'\n')
                f.write(u'--'*20 + u'\n')
        f.close()

    def reportAsCsv(self, tec, saveFile):
        with io.open(saveFile, 'w', encoding='utf-8') as f:
            f.write(toUnicode(MSG['msg17']) + ' : ' + '\n')

            if tec.mapUnit == 'meter':
                area_factor = 1.0E-6
                area_unit = u'km^2'
            elif tec.mapUnit == 'feet':
                area_factor = 1./43560
                area_unit = u'Acre'
            else:
                area_factor = 1.0
                area_unit = ''

            f.write(toUnicode(MSG['msg18']) + u',' +
                    unicode('%10.3f' % (tec.totalArea*area_factor) +
                            u',' + area_unit + u'\n'))
            f.write(u'\n')
            f.write(toUnicode(MSG['msg19']) + u',' +
                    unicode('%10.3f' % tec.glideRatio) + u'\n')
            f.write(toUnicode(MSG['msg20']) + u',' +
                    unicode('%10.3f' % tec.riffleRatio) + u'\n')
            f.write(toUnicode(MSG['msg21']) + u',' +
                    unicode('%10.3f' % tec.poolRatio) + u'\n')
            f.write(toUnicode(MSG['msg22']) + u',' +
                    unicode('%10.3f' % tec.runRatio) + u'\n')
            f.write(u'\n')

            f.write(toUnicode(MSG['msg23']) + u',' +
                    unicode('%10.3f' % tec.divIndex) + u'\n')
            f.write(u'\n')
            f.write(u'\n')

            for i in range(0, len(tec.specieWUA)):
                name = tec.specieWUA[i]['name']
                f.write(toUnicode(name) + u'\n')
                f.write(toUnicode(MSG['msg13']) + u'\n')
                f.write(u'\n')

                f.write(toUnicode(MSG['msg14']) + u',' +
                        unicode('%10.3f' % (tec.specieWUA[i]['WUAsimple']*area_factor)) +
                        u',' + area_unit+ u'\n')
                f.write(toUnicode(MSG['msg24']) + u',' +
                        unicode('%10.3f' % (tec.specieWUA[i]['WUAsimple']/tec.totalArea))
                        + u'\n')
                f.write(u'\n')
                f.write(toUnicode(MSG['msg15']) + u',' +
                        unicode('%10.3f' % (tec.specieWUA[i]['WUAarith']*area_factor)) +
                        u',' + area_unit+ u'\n')
                f.write(toUnicode(MSG['msg24']) + u',' +
                        unicode('%10.3f' % (tec.specieWUA[i]['WUAarith']/tec.totalArea)) +
                        u'\n')
                f.write(u'\n')
                f.write(toUnicode(MSG['msg16']) + u',' +
                        unicode('%10.3f' % (tec.specieWUA[i]['WUAharmonic']*area_factor)) +
                        u',' + area_unit + u'\n')
                f.write(u'\n')
                f.write(toUnicode(MSG['msg24']) + u',' +
                        unicode('%10.3f' % (tec.specieWUA[i]['WUAharmonic']/tec.totalArea)) +
                        u'\n')
                f.write(u'\n')
                f.write(u'\n')
        f.close()

    def genReport(self):
        tec = self.tecItemList.currentItem()

        projFolder = self.settings.value('projFolder')
        saveFile = QFileDialog.getSaveFileName(filter=self.tr('*.txt;; *.csv'),
                                               directory=projFolder)
        if saveFile.endswith('.txt'):
            self.reportAsTxt(tec, saveFile)
        elif saveFile.endswith('.csv'):
            self.reportAsCsv(tec, saveFile)
        else:
            QMessageBox(QMessageBox.Critical, title=toUnicode(MSG['msg26']),
                        text=toUnicode(MSG['msg25']))

    def showTECResult(self, tec):
        if tec.mapUnit == 'meter':
            area_factor = 1.0E-6
            area_unit = self.tr('km<sup>2</sup>')
        elif tec.mapUnit == 'feet':
            area_factor = 1./43560
            area_unit = 'Acre'
        else:
            area_factor = 1.0
            area_unit = ''

        self.reportTab.clear()

        browser0 = QTextBrowser()
        browser0.append('\n')
        browser0.append(toUnicode(MSG['msg18']) + u' : ' +
                        '%10.3f' % (tec.totalArea*area_factor) +
                        ' ' + area_unit + '\n')
        browser0.append(toUnicode(MSG['msg19']) + u' : ' +
                        '%10.3f' % tec.glideRatio)
        browser0.append(toUnicode(MSG['msg20']) + u' : ' +
                        '%10.3f' % tec.riffleRatio)
        browser0.append(toUnicode(MSG['msg21']) + u' : ' +
                        '%10.3f' % tec.poolRatio)
        browser0.append(toUnicode(MSG['msg22']) + u' : ' +
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
                '%10.3f' % (tec.specieWUA[i]['WUAsimple']*area_factor) +
                ' ' + area_unit)
            browser.append(
                toUnicode(MSG['msg24']) + ' ' +
                '%10.3f' % (tec.specieWUA[i]['WUAsimple']/tec.totalArea)
                + '\n')
            browser.append(
                toUnicode(MSG['msg15']) + ' ' +
                '%10.3f' % (tec.specieWUA[i]['WUAarith']*area_factor) +
                ' ' + area_unit)
            browser.append(
                toUnicode(MSG['msg24']) + ' ' +
                '%10.3f' % (tec.specieWUA[i]['WUAarith']/tec.totalArea) + '\n')
            browser.append(
                toUnicode(MSG['msg16']) + ' ' +
                '%10.3f' % (tec.specieWUA[i]['WUAharmonic']*area_factor) +
                ' ' + area_unit)
            browser.append(
                toUnicode(MSG['msg24']) + ' ' +
                '%10.3f' % (tec.specieWUA[i]['WUAharmonic']/tec.totalArea) +
                '\n')

            newWidget = QWidget()
            newWidget.setLayout(vLayout)
            self.reportTab.addTab(newWidget, name)

    def run(self):
        self.show()
        result = self.exec_()
        if result:
            pass
