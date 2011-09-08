# -*- coding: utf-8 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from ui_profileexportdialogbase import Ui_ProfileExportDialogBase

class ProfileExportDialog( QDialog,  Ui_ProfileExportDialogBase):
    
    def __init__(self,  iface):
        QDialog.__init__(self, None)
        self.setupUi(self)
        self.mIface = iface
        self.setupRasterComboBox()
        settings = QSettings()
        self.mPointDistanceSpinBox.setValue( settings.value( "/profileexport/pointdistance",  4.0 ).toDouble()[0] )
        self.mMaxValueDifferenceSpinBox.setValue( settings.value( "/profileexport/maxvaluediff",  5.0 ).toDouble()[0] )
        self.mButtonBox.button( QDialogButtonBox.Ok ).setEnabled( False ) #will be enabled once a valid output filename is given
        QObject.connect( self.mOutputFileLineEdit,  SIGNAL("textChanged(const QString&)"),  self.checkValidOutputDir )
        
    def setupRasterComboBox(self):
        layerMap = QgsMapLayerRegistry.instance().mapLayers()
        for layer in layerMap:
            mapLayer = layerMap[layer]
            if mapLayer.type() == QgsMapLayer.RasterLayer:
                self.mRasterLayerComboBox.addItem( mapLayer.name(),  layer )
                
    def rasterLayer(self):
        return self.mRasterLayerComboBox.itemData( self.mRasterLayerComboBox.currentIndex() ).toString()
        
    def pointDistance(self):
        return self.mPointDistanceSpinBox.value()
        
    def maxValueTolerance(self):
        return self.mMaxValueDifferenceSpinBox.value()
        
    def outputFile(self):
        return self.mOutputFileLineEdit.text()
        
    @pyqtSignature('') #avoid two connections
    def on_mOutputFileToolButton_clicked(self):
        settings = QSettings()
        outputFilePath = QFileDialog.getSaveFileName( None,  QCoreApplication.translate( "ProfileExportDialog","Select profile output file" ),  settings.value("/profileexport/outputdir",  "").toString(), "XML files (*.xml *.XML)" )
        if not outputFilePath.isNull():
            outputFileInfo = QFileInfo( outputFilePath)
            if outputFileInfo.suffix().isEmpty():
                outputFilePath.append(".xml")
            self.mOutputFileLineEdit.setText( outputFilePath )
            settings.setValue("/profileexport/outputdir",  outputFileInfo.absolutePath() )
            #self.mButtonBox.button( QDialogButtonBox.Ok ).setEnabled( True )
            
    @pyqtSignature('') #avoid two connections
    def on_mButtonBox_accepted(self):
        settings = QSettings()
        settings.setValue("/profileexport/pointdistance",  self.mPointDistanceSpinBox.value() )
        settings.setValue("/profileexport/maxvaluediff",  self.mMaxValueDifferenceSpinBox.value() )
    
    def checkValidOutputDir(self,  text ):
        if text.isEmpty():
            return
            
        fileInfo = QFileInfo( self.mOutputFileLineEdit.text() )
        #enable ok button only if save directory exists
        self.mButtonBox.button( QDialogButtonBox.Ok ).setEnabled( fileInfo.absoluteDir().exists() )
            