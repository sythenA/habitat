# -*- coding: utf-8 -*-

from habitat.specieItem import specieItem
from habitat.habitatTEC import TECfile
from habitat.toUnicode import toUnicode
from habitat.readSpecieXls import readXls
from habitat.reportPage import habitatReport

species = readXls(toUnicode('D:\水規所計畫\生態適合度模組\大安溪適合度曲線.xlsx'))
specie = specieItem(toUnicode(species[0][0][13]), species[0])
tecItem = TECfile(None, 0, 'D:\\test\\proj23\\proj23_TEC12.dat', iface)
tecItem.settings.setValue('x_Attr', 'Vel_X_m_p_s')
tecItem.settings.setValue('y_Attr', 'Vel_Y_m_p_s')
tecItem.settings.setValue('dep_Attr', 'Water_Depth_m')
tecItem.settings.setValue('bedDiaAttr', 'D50_mm')

# flowFitness, depthFitness, bedFitness = tecItem.fitness(specie)
# tecItem.fitnessByMesh(flowFitness, depthFitness, bedFitness)
# tecItem.divergence()

rep = habitatReport(iface, [tecItem], [specie])
rep.run()