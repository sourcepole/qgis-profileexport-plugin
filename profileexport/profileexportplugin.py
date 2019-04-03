# -*- coding: utf-8 -*-
from PyQt5.QtCore import QCoreApplication, QFile, QIODevice, QObject, QTextStream
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QDialog, QMessageBox
from PyQt5.QtXml import QDomDocument, QDomElement
from qgis.core import *
from qgis.gui import *
import math
from .profileexportdialog import ProfileExportDialog
from .resources_rc import *

class ProfileExportPlugin:
    def __init__(self, iface ):
        self.mIface = iface
        
    def initGui(self):
        self.mAction = QAction( QIcon(":/plugins/profileexport/seilkran.jpg"), "Profile export",  self.mIface.mainWindow() )
        self.mAction.triggered.connect( self.run )
        self.mIface.addToolBarIcon( self.mAction )
        
    def unload(self):
        self.mIface.removeToolBarIcon( self.mAction )
        
    def run(self):
        print( 'run' )
        
        currentMapLayer = self.mIface.mapCanvas().currentLayer()
        if currentMapLayer is None:
            QMessageBox.critical( None,  QCoreApplication.translate("ProfileExportPlugin","No current layer"),  QCoreApplication.translate("ProfileExportPlugin", "There is no current layer. Please highlight a layer in the legend") )
            return
        
        if not currentMapLayer.type() == QgsMapLayer.VectorLayer:
            QMessageBox.critical( None,  QCoreApplication.translate("ProfileExportPlugin", "Not a vector layer"),  QCoreApplication.translate("ProfileExportPlugin", "The profile export tool needs a selected line in the current vector layer") )
            return
            
        if currentMapLayer.selectedFeatureCount() != 1:
            QMessageBox.critical( None,  QCoreApplication.translate( "ProfileExportPlugin", "Profile tool needs a single selected feature"),  QCoreApplication.translate("ProfileExportPlugin","Please select the line describing the profile and run the export profile tool again") )
            return
        
        #geometry needs to be a line
        selectedFeature = currentMapLayer.selectedFeatures()[0]
        profileGeometry = selectedFeature.geometry()
        profileGeometry.convertToSingleType()
        if QgsWkbTypes.flatType( profileGeometry.wkbType() ) != QgsWkbTypes.LineString:
            QMessageBox.critical( None,  QCoreApplication.translate( "ProfileExportPlugin", "Selected feature is not a linestring"),  QCoreApplication.translate( "ProfileExportPlugin", "Please select a single linestring and run the export profile tool again") )
            return
        
        profilePolyLine = profileGeometry.asPolyline()
        if len(profilePolyLine) < 2:
            QMessageBox.critical( None,  QCoreApplication.translate( "ProfileExportPlugin", "Not enough vertices" ),  QCoreApplication.translate( "ProfileExportPlugin", "The profile export plugin needs a line with two vertices") )
            return
        elif len(profilePolyLine) > 2:
            QMessageBox.warning( None,  QCoreApplication.translate( "ProfileExportPlugin", "Line has more than two vertices" ),  QCoreApplication.translate( "ProfileExportPlugin", "The selected line has more than two vertices. Only the first and the second are considered for profile computation") )
        
        startPoint = profilePolyLine[0]
        #print( startPoint )
        endPoint = profilePolyLine[1]
        #print( endPoint )
        
        #get input/output file, point distance, value tolerance
        dialog = ProfileExportDialog( self.mIface )
        if dialog.exec_() == QDialog.Accepted:
            rasterLayer = QgsProject.instance().mapLayer( dialog.rasterLayer() )
            if rasterLayer is None:
                QMessageBox.critical( None,  QCoreApplication.translate( "ProfileExportPlugin", "Raster layer invalid"),  QCoreApplication.translate( "ProfileExportPlugin", "The selected raster layer could not be loaded") )
                return
            
            #reproject startPoint, endPoint if they are not in the raster CRS
            if rasterLayer.crs() != currentMapLayer.crs():
                profileCoordTrans = QgsCoordinateTransform( currentMapLayer.crs(), rasterLayer.crs(), QgsProject.instance().transformContext() )
                startPoint = profileCoordTrans.transform( startPoint.x(), startPoint.y() )
                endPoint = profileCoordTrans.transform( endPoint.x(), endPoint.y() )
            
            self.writeOutputFile( rasterLayer,  dialog.outputFile(),  dialog.pointDistance(),  dialog.maxValueTolerance(),  startPoint,  endPoint )
            
    def writeOutputFile(self,  rasterLayer,  outputFile,  pointDistance,  maxValueTolerance,  startPoint,  endPoint):
        resultXmlDocument = QDomDocument()
        encodingInstruction = resultXmlDocument.createProcessingInstruction( "encoding",  "UTF-8" )
        resultXmlDocument.appendChild( encodingInstruction )
        documentElement = resultXmlDocument.createElement("VFPData")
        resultXmlDocument.appendChild( documentElement )
        
        #profile length
        profileTotalDx = endPoint.x() - startPoint.x()
        profileTotalDy = endPoint.y() - startPoint.y()
        profileLength = math.sqrt( profileTotalDx * profileTotalDx + profileTotalDy * profileTotalDy )
        
        #single step
        dx = profileTotalDx / profileLength * pointDistance
        dy = profileTotalDy / profileLength * pointDistance
        
        dist = 0.0
        lastDist = 0.0
        currentValue = 0.0
        firstZ = self.firstRasterBandValue( startPoint ,  rasterLayer )
        if firstZ is None: #makes only sense if initial z is set
            QMessageBox.critical( None,  QCoreApplication.translate( "ProfileExportPlugin", "First z value invalid"),  QCoreApplication.translate( "ProfileExportPlugin", "The first z-Value of the profile is invalid. Please make sure the profile start point is on the elevation model") )
            return
        lastValue = firstZ
        currentX = startPoint.x()
        currentY = startPoint.y()
        while dist < profileLength:
            currentValue = self.firstRasterBandValue( QgsPointXY( currentX,  currentY ),  rasterLayer )
            
            #elevation tolerance between two points exceeded. Insert additional points
            if not currentValue is None and not lastValue is None and ( currentValue - lastValue ) > maxValueTolerance: 
                nIntermediatePoints = int( (currentValue - lastValue ) / maxValueTolerance)
                dIntermediatePointDist = math.sqrt(  ( dx / (nIntermediatePoints + 1) ) * ( dx / (nIntermediatePoints + 1) ) + ( dy / (nIntermediatePoints + 1) ) * ( dy / (nIntermediatePoints + 1) ) )
                lastIntermediateValue = lastValue
                for i in range( nIntermediatePoints ):
                    #print 'inserting additional point'
                    dxIntermediate =  dx / ( nIntermediatePoints + 1 ) * ( i+1 )
                    dyIntermediate = dy / ( nIntermediatePoints + 1 ) * ( i + 1 )
                    xIntermediate = currentX - dx + dxIntermediate
                    yIntermediate = currentY - dy + dyIntermediate
                    intermediateDist = math.sqrt( dxIntermediate * dxIntermediate + dyIntermediate * dyIntermediate )
                    currentIntermediateValue = self.firstRasterBandValue( QgsPointXY( xIntermediate,  yIntermediate ),  rasterLayer )
                    if not currentIntermediateValue is None and not lastIntermediateValue is None:
                        self.addElevationPoint( resultXmlDocument,  documentElement, dist - pointDistance + intermediateDist,  dIntermediatePointDist,    currentIntermediateValue - lastIntermediateValue,  currentIntermediateValue - firstZ,  xIntermediate, yIntermediate )
                    lastIntermediateValue = currentIntermediateValue
                    lastDist = dist - pointDistance + intermediateDist
            
            if not currentValue is None and not lastValue is None:
                self.addElevationPoint( resultXmlDocument,  documentElement,  dist,  dist - lastDist,  currentValue - lastValue,  currentValue - firstZ,  currentX,  currentY )
            currentX += dx
            currentY += dy
            lastDist = dist
            dist += pointDistance
            lastValue = currentValue
            
        #last value normally does not fit into the point interval
        if currentX != endPoint.x() or currentY != entPoint.y():
            currentValue = self.firstRasterBandValue( endPoint,  rasterLayer )
            if not currentValue is None:
                self.addElevationPoint( resultXmlDocument,  documentElement,  profileLength,  pointDistance - ( dist - profileLength ), currentValue - lastValue,  currentValue - firstZ,  endPoint.x(),  endPoint.y()  )
            
        #write dom document to file
        resultXmlFile = QFile( outputFile )
        if not resultXmlFile.open( QIODevice.WriteOnly ):
            QMessageBox.critical( None,  QCoreApplication.translate( "ProfileExportPlugin","Error"),  QCoreApplication.translate( "ProfileExportPlugin","The output file could not be written to disk") )
            return
        
        resultTextStream = QTextStream( resultXmlFile )
        resultTextStream.setCodec("UTF-8")
        resultTextStream.__lshift__( resultXmlDocument.toString() )
        resultXmlFile.close()
        QMessageBox.information( None,  QCoreApplication.translate( "ProfileExportPlugin","Export finished"),  QCoreApplication.translate( "ProfileExportPlugin", "The profile export is successfully finished"))
            
    
        
    def addElevationPoint(self,  xmlDoc,  parentElement,  totDist,  dist,  dz,  z,  wgs_x,  wgs_y):  
        importGisElem = xmlDoc.createElement("import_gis")
        #dist
        distElem = xmlDoc.createElement("dist")
        distElemText = xmlDoc.createTextNode( "{0:f}".format( totDist ) )
        distElem.appendChild( distElemText)
        importGisElem.appendChild( distElem )
        #z0
        z0Elem = xmlDoc.createElement("z0")
        z0ElemText = xmlDoc.createTextNode( "{0:f}".format( z ) )
        z0Elem.appendChild( z0ElemText )
        importGisElem.appendChild( z0Elem )
        #entfernung
        entfElem = xmlDoc.createElement("entfernung")
        entfElemText = xmlDoc.createTextNode( "{0:f}".format( dist ) )
        entfElem.appendChild( entfElemText )
        importGisElem.appendChild( entfElem )
        #höhe
        hoeheElem = xmlDoc.createElement(u"höhe" )
        hoeheElemText = xmlDoc.createTextNode( "{0:f}".format( dz) )
        hoeheElem.appendChild( hoeheElemText )
        importGisElem.appendChild( hoeheElem )
        #koord_e
        koordEElem = xmlDoc.createElement("koord_e")
        koordEElemText = xmlDoc.createTextNode( "{0:.8f}".format( wgs_x ) )
        koordEElem.appendChild( koordEElemText)
        importGisElem.appendChild( koordEElem )
        #koord_n
        koordNElem = xmlDoc.createElement("koord_n")
        koordNElemText = xmlDoc.createTextNode( "{0:.8f}".format( wgs_y ) )
        koordNElem.appendChild( koordNElemText )
        importGisElem.appendChild( koordNElem )
        
        parentElement.appendChild( importGisElem )
        
        
    
    def firstRasterBandValue(self,  point,  rasterLayer):
        identifyResult = rasterLayer.dataProvider().identify( point, QgsRaster.IdentifyFormatValue )

        if not identifyResult.isValid():
            return -9999
        results = identifyResult.results()
        return results[1]
