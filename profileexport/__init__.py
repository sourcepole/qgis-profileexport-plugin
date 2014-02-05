# -*- coding: utf-8 -*-
"""
***************************************************************************
    Profile Export
    A plugin to export raster profiles to xml files
    ---------------------
    Copyright            : (C) 2011-2014 by Sourcepole
    Email                : qgis at sourcepole dot ch
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

def classFactory(iface):
    from profileexportplugin import ProfileExportPlugin
    return ProfileExportPlugin(iface)
