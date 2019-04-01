from PyQt5.QtCore import QCoreApplication, QFileInfo, QSettings
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QFileDialog
from qgis.core import *
import os
from qgis.PyQt import uic

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'profileexportdialogbase.ui'))

class ProfileExportDialog( QDialog, FORM_CLASS ):
    
    def __init__(self, iface, parent=None):
        super(ProfileExportDialog, self).__init__(parent)
        self.setupUi(self)
        self.mIface = iface
        self.setupRasterComboBox()
        settings = QSettings()
        self.mPointDistanceSpinBox.setValue( settings.value( "/profileexport/pointdistance",  4.0 ) )
        self.mMaxValueDifferenceSpinBox.setValue( settings.value( "/profileexport/maxvaluediff",  5.0 ) )
        self.mButtonBox.button( QDialogButtonBox.Ok ).setEnabled( False ) #will be enabled once a valid output filename is given
        self.mOutputFileLineEdit.textChanged.connect( self.checkValidOutputDir )
        self.mOutputFileToolButton.clicked.connect( self.selectOutputFile )
        
    def setupRasterComboBox(self):
        layerMap = QgsProject.instance().mapLayers()
        for layer in layerMap:
            mapLayer = layerMap[layer]
            if mapLayer.type() == QgsMapLayer.RasterLayer:
                self.mRasterLayerComboBox.addItem( mapLayer.name(), layer )
                
    def checkValidOutputDir(self,  text ):
        if not text:
            return
            
        fileInfo = QFileInfo( self.mOutputFileLineEdit.text() )
        #enable ok button only if save directory exists
        self.mButtonBox.button( QDialogButtonBox.Ok ).setEnabled( fileInfo.absoluteDir().exists() )
        
    def selectOutputFile(self):
        settings = QSettings()
        outputFilePath = QFileDialog.getSaveFileName( None,  QCoreApplication.translate( "ProfileExportDialog","Select profile output file" ),  settings.value("/profileexport/outputdir",  ""), "XML files (*.xml *.XML)" )[0]
        if outputFilePath:
            outputFileInfo = QFileInfo( outputFilePath )
            if not outputFileInfo.suffix():
                outputFilePath.append(".xml")
            self.mOutputFileLineEdit.setText( outputFilePath )
            settings.setValue("/profileexport/outputdir",  outputFileInfo.absolutePath() )
            
    def rasterLayer(self):
        return self.mRasterLayerComboBox.itemData( self.mRasterLayerComboBox.currentIndex() )
        
    def pointDistance(self):
        return self.mPointDistanceSpinBox.value()
        
    def maxValueTolerance(self):
        return self.mMaxValueDifferenceSpinBox.value()
        
    def outputFile(self):
        return self.mOutputFileLineEdit.text()
            
