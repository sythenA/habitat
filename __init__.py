# -*- coding: utf-8 -*-
"""
/***************************************************************************
 habitat
                                 A QGIS plugin
 Measuring habitat fitness for Taiwan unique species using SRH-2D results
                             -------------------
        begin                : 2018-09-13
        copyright            : (C) 2018 by Manysplendid co.
        email                : yengtinglin@manysplendid.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load habitat class from file habitat.

    :param iface: A QGIS interface instance.
    :type iface: QgisInterface
    """
    #
    from .habitatFitness import habitat
    return habitat(iface)
