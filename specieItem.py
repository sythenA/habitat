# -*- coding:utf-8 -*-

from qgis.PyQt.QtGui import QListWidgetItem
from qgis.PyQt.QtCore import Qt
from toUnicode import toUnicode
from msg import MSG
import re


class specieItem(QListWidgetItem):
    def __init__(self, specieName, specieDat, parent=None):
        super(specieItem, self).__init__(specieName, parent=parent)
        self.rawData = specieDat
        self.setCheckState(Qt.Unchecked)
        self.analyseData()

    def analyseData(self):
        rawData = self.rawData
        flowRaw = None
        depthRaw = None
        bedRaw = None

        for line in rawData:
            if toUnicode(line[7]) == toUnicode(MSG['msg03']):
                depthRaw = line[9]
                self.depthUnit = line[8]
            elif toUnicode(line[7]) == toUnicode(MSG['msg04']):
                flowRaw = line[9]
                self.flowUnit = line[8]
            elif toUnicode(line[7]) == toUnicode(MSG['msg05']):
                bedRaw = line[9]
                self.bedUnit = line[8]

        flowCategory = list()
        if flowRaw:
            flowRaw = re.split('[;]', flowRaw)
            for level in flowRaw:
                level = re.split('[,]', level)
                flowCategory.append([level[0], level[1], level[2]])
            self.flowCategory = flowCategory

        depthCategory = list()
        if depthRaw:
            depthRaw = re.split('[;]', depthRaw)
            for level in depthRaw:
                level = re.split('[,]', level)
                depthCategory.append([level[0], level[1], level[2]])
            self.depthCategory = depthCategory

        bedCategory = list()
        if bedRaw:
            bedRaw = re.split('[;]', bedRaw)
            for level in bedRaw:
                level = re.split('[,]', level)
                bedCategory.append([level[0], level[1], level[2]])
            self.bedCategory = bedCategory

        self.region = rawData[0][3]
        self.researcher = rawData[0][6]
        self.Efamily = rawData[0][10]
        self.family = rawData[0][11]
        self.BinoName = rawData[0][12]
        self.name = toUnicode(rawData[0][13])
        self.cName = re.split('[、]', rawData[0][14])
