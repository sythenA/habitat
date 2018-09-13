
from qgis.PyQt.QtGui import QListWidgetItem
from msg import MSG
import re


class specieItem(QListWidgetItem):
    def __init__(self, specieName, specieDat):
        super(specieItem, QListWidgetItem).__init__(text='specieName')
        self.rawData = specieDat
        self.analyseData

    def analyseData(self):
        rawData = self.rawData
        flowRaw = None
        depthRaw = None
        bedRaw = None

        for line in rawData:
            if line[7] == MSG['msg03']:
                depthRaw = line[9]
            elif line[7] == MSG['msg04']:
                flowRaw = line[9]
            elif line[7] == MSG['msg05']:
                bedRaw = line[9]

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
