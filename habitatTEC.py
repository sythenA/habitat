
from PyQt4.QtGui import QListWidgetItem
from qgis.core import QgsCoordinateReferenceSystem, QgsMapLayerRegistry
from qgis.core import QgsFields, QgsField, QgsProject, QgsRasterLayer, QGis
from qgis.core import QgsVectorFileWriter, QgsVectorLayer, QgsFeature
from qgis.core import QgsGeometry, QgsStyleV2, QgsRasterBandStats
from qgis.core import QgsColorRampShader, QgsSingleBandPseudoColorRenderer
from qgis.core import QgsRasterShader
from osgeo import osr, gdal
from gdalconst import GA_Update
from PyQt4.QtCore import QVariant, QFileInfo, QSettings, Qt
from math import ceil, sqrt
from shapely.ops import cascaded_union, polygonize
import numpy as np
from scipy.spatial import Delaunay
from scipy.interpolate import griddata
from toUnicode import toUnicode
import re
import subprocess
import os
import processing
import shapely.geometry as geometry


class TECfile(QListWidgetItem):
    def __init__(self, parent, widgetType, filePath, iface):
        super(TECfile, self).__init__(parent, widgetType)
        self.filePath = filePath
        self.fileName = os.path.basename(filePath)
        self.headerLinesCount = 0
        self.iface = iface
        self.TECTile = ''
        self.settings = QSettings('ManySplendid', 'HabitatFitness')
        self.variables = list()
        self.composition = dict()
        self.variableType = list()
        self.readTEC(filePath)
        self.specieWUA = list()
        self.outDir = ''
        self.xAttr = ''
        self.yAttr = ''

        self.iface = iface

        self.setText(os.path.basename(filePath))

    def readTEC(self, filePath):
        f = open(filePath)
        dat = f.readlines()
        self.getVariables(dat)
        self.readVariables(dat)
        self.dat = dat

    def loadTEC(self):
        self.readVariables(self.dat)

        for i in range(0, len(self.variables[3]['Water_Elev_m'])):
            if float(self.variables[3]['Water_Elev_m'][i]) == -999.0:
                self.variables[3][
                    'Water_Elev_m'][i] = self.variables[2]['Bed_Elev_meter'][i]

        Xkey = self.variables[0].keys()[0]
        X = self.toFloat(self.variables[0][Xkey])
        self.Xmax = max(X)
        self.Xmin = min(X)
        Ykey = self.variables[1].keys()[0]
        Y = self.toFloat(self.variables[1][Ykey])
        self.Ymax = max(Y)
        self.Ymin = min(Y)

        #  ########  Make Othogonal Grid Points  #########
        points2 = geometry.MultiPoint(list(zip(X, Y)))
        concave_hull2, edge_points2 = self.alpha_shape(points2, alpha=0.01)
        self.hull = concave_hull2
        reso = float(self.settings.value('resolution'))
        self.reso = reso

        X_coordinate = np.arange(self.Xmin, self.Xmax+0.001, reso)
        Y_coordinate = np.arange(self.Ymax, self.Ymin, -reso)
        self.Nx = len(X_coordinate)
        self.Ny = len(Y_coordinate)
        X_ref, Y_ref = np.meshgrid(X_coordinate, Y_coordinate)
        self.X_ref = X_ref
        self.Y_ref = Y_ref

        widx = np.zeros([self.Ny, self.Nx])

        # Identify points inside mesh area
        for i in range(0, len(X_ref)):
            for j in range(0, len(X_ref[0])):
                widx[i, j] = self.within_polygon(
                    geometry.Point(X_ref[i, j], Y_ref[i, j]), concave_hull2, 0)
        self.widx = widx

        # self.makeMeshLayer()
        # self.makeSieve()
        # self.genNodeLayer()

    def alpha_shape(self, points, alpha):
        """
        Compute the alpha shape (concave hull) of a set of points.

        @param points: Iterable container of points.
        @param alpha: alpha value to influence the gooeyness of the border.
                      Smaller numbers don't fall inward as much as larger
                      numbers. Too large, and you lose everything!
        """
        if len(points) < 4:
            # When you have a triangle, there is no sense in computing an alpha
            # shape.
            return geometry.MultiPoint(list(points)).convex_hull

        def add_edge(edges, edge_points, coords, i, j):
            """Add a line between the i-th and j-th points, if not in the list
            already"""
            if (i, j) in edges or (j, i) in edges:
                # already added
                return
            edges.add((i, j))
            edge_points.append(coords[[i, j]])

        coords = np.array([point.coords[0] for point in points])

        tri = Delaunay(coords)
        edges = set()
        edge_points = []
        # loop over triangles:
        # ia, ib, ic = indices of corner points of the triangle
        for ia, ib, ic in tri.vertices:
            pa = coords[ia]
            pb = coords[ib]
            pc = coords[ic]

            # Lengths of sides of triangle
            a = sqrt((pa[0]-pb[0])**2 + (pa[1]-pb[1])**2)
            b = sqrt((pb[0]-pc[0])**2 + (pb[1]-pc[1])**2)
            c = sqrt((pc[0]-pa[0])**2 + (pc[1]-pa[1])**2)

            # Semiperimeter of triangle
            s = (a + b + c)/2.0

            # Area of triangle by Heron's formula
            area = sqrt(s*(s - a)*(s - b)*(s - c))
            try:
                circum_r = a*b*c/(4.0*area)
            except(ZeroDivisionError):
                circum_r = 0

            # Here's the radius filter.
            # print circum_r
            if circum_r < 1.0/alpha:
                add_edge(edges, edge_points, coords, ia, ib)
                add_edge(edges, edge_points, coords, ib, ic)
                add_edge(edges, edge_points, coords, ic, ia)

        m = geometry.MultiLineString(edge_points)
        triangles = list(polygonize(m))
        return cascaded_union(triangles), edge_points

    def within_polygon(self, grid_point, concave_hull, buffer):
        intw = 0
        if grid_point.within(concave_hull.buffer(buffer)):
            intw = 1
        return intw

    def attributeList(self):
        attributes = self.attributes
        _attrs = list()
        for i in range(2, len(attributes)):
            _attrs.append([attributes[i], 0])
        self.attributes = _attrs

    def fitnessByMesh(self, flowFitness, depthFitness, bedFit):
        def singleMeshArea(oneMesh):
            areaSum = 0.
            for j in range(1, len(oneMesh)):
                areaSum += (oneMesh[j][1]*oneMesh[j-1][0] -
                            oneMesh[j][0]*oneMesh[j-1][1])
            return abs(areaSum)

        def simpleMean(depFit, flowFit, bedFit):
            if depFit > 0. and bedFit > 0.:
                return (depFit + flowFit + bedFit)/3.
            else:
                return (depFit + flowFit)/2.

        def arithMean(depFit, flowFit, bedFit):
            if bedFit > 0.:
                return (depFit*flowFit*bedFit)**(1./3)
            else:
                return sqrt(depFit*flowFit)

        def harmonicMean(depFit, flowFit, bedFit):
            if bedFit > 0.:
                try:
                    return 3./(1./depFit + 1./flowFit + 1./bedFit)
                except(ZeroDivisionError):
                    return 0.
            else:
                try:
                    return 2./(1./depFit + 1./flowFit)
                except(ZeroDivisionError):
                    return 0.

        WUAsimple = 0.
        WUAarith = 0.
        WUAharmonic = 0.

        mesh = self.mesh
        xKey = self.variables[0].keys()[0]
        yKey = self.variables[1].keys()[0]
        X = self.variables[0][xKey]
        Y = self.variables[1][yKey]

        for polygon in mesh:
            singleMesh = list()
            avgDepFit = 0.
            avgFlowFit = 0.
            avgBedFit = 0.
            if polygon[-1] == polygon[-2]:
                polygon[-1] = polygon[0]
            else:
                polygon.append(polygon[0])
            sumFlowFit = 0.
            sumDepFit = 0.
            sumBedFit = 0.
            for node in polygon:
                singleMesh.append((X[node-1], Y[node-1]))
            meshArea = singleMeshArea(singleMesh)
            for j in range(0, len(polygon)-1):
                node = polygon[j]
                sumFlowFit += flowFitness[node-1]
                sumDepFit += depthFitness[node-1]
                if self.useBed:
                    sumBedFit += bedFit[node-1]
            avgDepFit = sumDepFit/(len(polygon)-1)
            avgFlowFit = sumFlowFit/(len(polygon)-1)
            if self.useBed:
                avgBedFit = sumBedFit/(len(polygon)-1)
            WUAsimple += simpleMean(avgDepFit, avgFlowFit, avgBedFit)*meshArea
            WUAarith += arithMean(avgDepFit, avgFlowFit, avgBedFit)*meshArea
            WUAharmonic += harmonicMean(avgDepFit, avgFlowFit,
                                        avgBedFit)*meshArea
        # Calculate fitness in mesh
        return WUAsimple, WUAarith, WUAharmonic

    def getVariables(self, dat):
        def readDat(dat, title, _variable, ZONE, DT):
            mode = 0
            lineCount = 0
            for line in dat:
                if line.startswith(' TITLE'):
                    mode = 0
                elif line.startswith(' VARIABLES'):
                    mode = 1
                elif line.startswith(' ZONE'):
                    mode = 2
                elif line.startswith(' DT'):
                    mode = 3
                elif line.endswith(')\n'):
                    mode = 4

                if mode == 0:
                    title.append(line)
                elif mode == 1:
                    _variables.append(line)
                elif mode == 2:
                    ZONE.append(line)
                elif mode == 3 or mode == 4:
                    DT.append(line)
                    if line.endswith(')\n'):
                        mode = 5
                else:
                    return (title, _variable, ZONE, DT, lineCount)
                lineCount += 1

        title = list()
        _variables = list()
        ZONE = list()
        DT = list()

        title, _variables, ZONE, DT, lineCount = readDat(
            dat, title, _variables, ZONE, DT)

        self.headerLinesCount = lineCount

        titleString = ''
        for line in title:
            titleString += line

        titleString.replace('\n', '')
        titleString.replace('"', '')
        titleString = re.split('=', titleString)
        self.TECTitle = titleString[1].replace('\n', '').strip()

        variableString = ''
        for line in _variables:
            variableString += line
        variableString.replace('\n', '')
        self.variables = re.findall(r'\S+', variableString)
        self.attributes = re.findall(r'\S+', variableString)
        self.variables.pop(0)
        self.attributes.pop(0)
        self.variables[0] = self.variables[0].replace('=', '')
        self.attributes[0] = self.attributes[0].replace('=', '')
        self.attributeList()

        zoneString = ''
        for line in ZONE:
            zoneString += line
        zoneSplit = re.split(',', zoneString)
        zoneSplit[0] = zoneSplit[0].replace(' ZONE ', '')
        for unit in zoneSplit:
            self.composition.update({unit.split('=')[0]:
                                     unit.split('=')[1].strip()})

        DTstring = ''
        for line in DT:
            DTstring += line
        DTstring = DTstring.replace(' DT=(', '')
        DTstring = DTstring.replace(' \n', '')
        DTstring = DTstring.replace(')\n', '')
        vtype = re.split(r'\s', DTstring.strip())
        self.variableType = vtype

    def readVariables(self, dat):
        lineCounter = int(ceil(float(self.composition['N'])/5))
        variables = self.variables
        totalVaraibles = len(variables)

        readCounter = 0
        variableCounter = 0
        data = list()
        mesh = list()
        for i in range(self.headerLinesCount, len(dat)):
            row = re.findall(r'\S+', dat[i])
            for number in row:
                try:
                    data.append(float(number))
                except(ValueError):
                    data.append(0.0)

            readCounter += 1

            if ((readCounter == lineCounter) and
                    (variableCounter < totalVaraibles)):
                variables[variableCounter] = {str(variables[variableCounter]):
                                              data}
                variableCounter += 1
                data = list()
                readCounter = 0
            elif variableCounter >= totalVaraibles:
                polygon = list()
                for node in dat[i].split():
                    polygon.append(int(node))
                mesh.append(polygon)
        self.mesh = mesh

    def toFloat(self, array):
        for i in range(0, len(array)):
            array[i] = float(array[i])

        return array

    def getAttrIdx(self, attr):
        variables = self.variables

        for idx in range(0, len(variables)):
            if attr == variables[idx].keys()[0]:
                return idx
        return -1

    def depthData(self, depthIdx, depthUnit):
        def changeOfUnit(data, unit):
            if unit == 'cm':
                return data
            elif unit == 'm':
                for dep in data:
                    dep = dep*100.
                return data
            elif unit == 'mm':
                for dep in data:
                    dep = dep/10.
                return data
            elif unit == 'ft.':
                for dep in data:
                    dep = dep*30.48
                return data
            elif unit == 'in.':
                for dep in data:
                    dep = dep*2.54
                return data

        depKey = self.variables[depthIdx].keys()[0]
        depData = self.variables[depthIdx][depKey]
        depthUnit = self.settings.value('depthUnit')
        depData = changeOfUnit(depData, depthUnit)

        return depData

    def flowSpeedData(self, xAttrIdx, yAttrIdx, xUnit, yUnit):
        def changeOfUnit(data, unit):
            if unit == 'm/s':
                return data
            elif unit == 'cm/s':
                for speed in data:
                    speed = speed/100.
                return data
            elif unit == 'm/min':
                for speed in data:
                    speed = speed/60.
                return data
            elif unit == 'cm/min':
                for speed in data:
                    speed = speed/60./100.
                return data
            elif unit == 'in/s':
                for speed in data:
                    speed = speed/39.370
                return data
            elif unit == 'in/min':
                for speed in data:
                    speed = speed/39.370/60.
                return data
            elif unit == 'ft/s':
                for speed in data:
                    speed = speed*0.3048
                return data
            elif unit == 'ft/min':
                for speed in data:
                    speed = speed*0.3048/60.
                return data

        xDirKey = self.variables[xAttrIdx].keys()[0]
        yDirKey = self.variables[yAttrIdx].keys()[0]
        xData = self.variables[xAttrIdx][xDirKey]
        yData = self.variables[yAttrIdx][yDirKey]

        xData = changeOfUnit(xData, xUnit)
        yData = changeOfUnit(yData, yUnit)

        speedMag = list()
        for i in range(0, len(xData)):
            speedMag.append(sqrt(xData[i]**2 + yData[i]**2))

        return speedMag

    def categoryVal(self, data, category):
        fitnessMat = list()
        for j in range(0, len(data)):
            fitNess = 0.
            for k in range(0, len(category)):
                if data[j] >= category[k][0] and data[j] < category[k][1]:
                    fitNess = category[k][2]
            fitnessMat.append(fitNess)
        return fitnessMat

    def divergence(self):
        # glide : 1
        # pool : 2
        # riffle : 3
        # run : 4

        def singleMeshArea(oneMesh):
            # use shoelace equation to calculate mesh area
            areaSum = 0.
            for j in range(1, len(oneMesh)):
                areaSum += (oneMesh[j][1]*oneMesh[j-1][0] -
                            oneMesh[j][0]*oneMesh[j-1][1])
            return areaSum

        def meshType(aveFlow, aveDepth):
            if aveFlow > 0. and aveFlow <= 0.3:
                if aveDepth > 0. and aveDepth <= 0.3:
                    return 1
                elif aveDepth > 0.3:
                    return 2
            elif aveFlow > 0.3:
                if aveDepth > 0. and aveDepth <= 0.3:
                    return 3
                elif aveDepth > 0.3:
                    return 4
            return 0

        depthIdx = self.getAttrIdx(self.settings.value('depAttr'))
        depthUnit = self.settings.value('depthUnit')
        xDirIdx = self.getAttrIdx(self.settings.value('xAttr'))
        xUnit = self.settings.value('xDirUnit')
        yDirIdx = self.getAttrIdx(self.settings.value('yAttr'))
        yUnit = self.settings.value('yDirUnit')
        depData = self.depthData(depthIdx, depthUnit)
        flowData = self.flowSpeedData(xDirIdx, yDirIdx, xUnit, yUnit)

        # Get mesh (For area calculation)
        mesh = self.mesh
        xKey = self.variables[0].keys()[0]
        yKey = self.variables[1].keys()[0]
        X = self.variables[0][xKey]
        Y = self.variables[1][yKey]

        areaGlide = 0.
        areaPool = 0.
        areaRiffle = 0.
        areaRun = 0.
        totalArea = 0.
        for polygon in mesh:
            sumFlow = 0.
            sumDepth = 0.
            points = list()
            for k in range(0, len(polygon)-1):
                node = polygon[k]
                sumFlow += flowData[node-1]
                sumDepth += depData[node-1]
            for j in range(0, len(polygon)):
                node = polygon[j]
                points.append([X[node-1], Y[node-1]])
            oneMeshArea = singleMeshArea(points)
            avgFlow = sumFlow/(len(polygon)-1)
            avgDepth = sumDepth/(len(polygon)-1)

            _type = meshType(avgFlow, avgDepth)

            if _type == 1:
                areaGlide += oneMeshArea
            elif _type == 2:
                areaPool += oneMeshArea
            elif _type == 3:
                areaRiffle += oneMeshArea
            elif _type == 4:
                areaRun += oneMeshArea

            if _type > 0:
                totalArea += oneMeshArea

        self.glideRatio = areaGlide/totalArea
        self.poolRatio = areaPool/totalArea
        self.riffleRatio = areaRiffle/totalArea
        self.runRatio = areaRun/totalArea
        self.totalArea = totalArea

        advIndex = (self.glideRatio**2 + self.poolRatio**2 +
                    self.riffleRatio**2 + self.runRatio**2)
        divIndex = 1 - advIndex

        self.divIndex = divIndex

    def fitness(self, specieItem):
        useBedData = False

        depthIdx = self.getAttrIdx(self.settings.value('depAttr'))
        depthUnit = self.settings.value('depthUnit')
        xDirIdx = self.getAttrIdx(self.settings.value('xAttr'))
        xUnit = self.settings.value('xDirUnit')
        yDirIdx = self.getAttrIdx(self.settings.value('yAttr'))
        yUnit = self.settings.value('yDirUnit')
        if self.settings.value('useBedDia') == Qt.Checked:
            useBedData = True
            self.useBed = True
            bedDiaIdx = self.getAttrIdx(self.settings.value('bedDiaAttr'))
            bedKey = self.variables[bedDiaIdx].keys()[0]
            bedData = self.variables[bedDiaIdx][bedKey]
        depData = self.depthData(depthIdx, depthUnit)
        speedData = self.flowSpeedData(xDirIdx, yDirIdx, xUnit, yUnit)

        flowCategory = specieItem.flowCategoryMPS()
        flowFitness = self.categoryVal(speedData, flowCategory)
        depthCategory = specieItem.depthCategoryM()
        depthFitness = self.categoryVal(depData, depthCategory)
        bedFitness = list()

        if specieItem.bedCategory:
            bedCategory = specieItem.bedCategory
            if useBedData:
                bedFitness = self.categoryVal(bedData, bedCategory)

        # If bed diameter fitness not used, return an empty list
        return flowFitness, depthFitness, bedFitness
