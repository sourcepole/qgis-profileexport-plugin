# -*- coding: utf-8 -*-
from PyQt4.QtCore import *
from profileexportplugin import ProfileExportPlugin
import locale
import os

#support for multiple languages
translator = QTranslator(QCoreApplication.instance())
localeCode = locale.getlocale()[0]
if localeCode:
    translator.load("profileexport_" + locale.getlocale()[0] + ".qm",  os.path.dirname(__file__))
    QCoreApplication.instance().installTranslator(translator)

def name():
    return QCoreApplication.translate("init","Profile export")

def description():
    return QCoreApplication.translate("init","A plugin to export raster profiles to xml files")

def version():
    return "0.21"
    
def icon():
	return "seilkran.jpg"

def qgisMinimumVersion():
    return "1.7"

def authorName():
    return "Sourcepole"

def classFactory(iface):
    return ProfileExportPlugin(iface)
