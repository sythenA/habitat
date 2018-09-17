# coding: utf-8
import xlrd
from operator import itemgetter
from toUnicode import toUnicode


def readXls(xlsFile):
    data = xlrd.open_workbook(toUnicode(xlsFile))
    table = data.sheets()[0]
    raw_data = list()
    for j in range(0, table.nrows):
        raw_data.append(table.row_values(j))
    raw_data.pop(0)
    raw_data = sorted(raw_data, key=itemgetter(12))

    data_by_specie = list()
    specie = list()
    specie.append(raw_data[0])
    for j in range(1, len(raw_data)):
        if raw_data[j][12] == raw_data[j-1][12]:
            specie.append(raw_data[j])
        else:
            data_by_specie.append(specie)
            specie = list()
            specie.append(raw_data[j])
    data_by_specie.append(specie)

    for specie in data_by_specie:
        _specie = list()
        fType = list()
        for line in specie:
            if line[7] not in fType:
                fType.append(line[7])
                _specie.append(line)
        idx = data_by_specie.index(specie)
        data_by_specie[idx] = _specie

    return data_by_specie
