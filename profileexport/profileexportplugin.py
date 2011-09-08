# -*- coding: utf-8 -*-

from qgis.core import *
from qgis.gui import  *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtXml import *
import math
import resources
from profileexportdialog import ProfileExportDialog

class ProfileExportPlugin:
    
    def __init__(self,  iface):
        self.mIface = iface
        
    def initGui(self):
        self.mAction = QAction( QIcon(":/plugins/profileexport/seilkran.jpg"), "Profile export",  self.mIface.mainWindow() )
        QObject.connect(self.mAction, SIGNAL("triggered()"), self.run)
        self.mIface.addToolBarIcon( self.mAction )
        
    def unload(self):
        self.mIface.removeToolBarIcon( self.mAction )
        
    def run(self):
        #get startpoint / endpoint from selected feture and bail out in case of error
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
            
        selectedFeature = QgsFeature()
        selectedFeatureId = currentMapLayer.selectedFeaturesIds()[0]
        currentMapLayer.featureAtId(selectedFeatureId,  selectedFeature, True,  False )
        #profileGeometry = currentMapLayer.selectedFeatures()[0].geometry()
        profileGeometry = selectedFeature.geometry()
        #print profileGeometry
        #print profileGeometry.exportToWkt()
        
        #geometry needs to be a line
        if profileGeometry.wkbType() != QGis.WKBLineString:
            QMessageBox.critical( None,  QCoreApplication.translate( "ProfileExportPlugin", "Selected feature is not a linestring"),  QCoreApplication.translate( "ProfileExportPlugin", "Please select a single linestring and run the export profile tool again") )
            return
            
        profilePolyLine = profileGeometry.asPolyline()
        if len(profilePolyLine) < 2:
            QMessageBox.critical( None,  QCoreApplication.translate( "ProfileExportPlugin", "Not enough vertices" ),  QCoreApplication.translate( "ProfileExportPlugin", "The profile export plugin needs a line with two vertices") )
            return
        elif len(profilePolyLine) > 2:
            QMessageBox.warning( None,  QCoreApplication.translate( "ProfileExportPlugin", "Line has more than two vertices" ),  QCoreApplication.translate( "ProfileExportPlugin", "The selected line has more than two vertices. Only the first and the second are considered for profile computation") )
        
        startPoint = profilePolyLine[0]
        #print startPoint
        endPoint = profilePolyLine[1]
        #print endPoint
        
        #get input/output file, point distance, value tolerance
        dialog = ProfileExportDialog( self.mIface )
        if dialog.exec_() == QDialog.Accepted:
            self.writeOutputFile( dialog.rasterLayer(),  dialog.outputFile(),  dialog.pointDistance(),  dialog.maxValueTolerance(),  startPoint,  endPoint )
    
    def writeOutputFile(self,  inputRaster,  outputFile,  pointDistance,  maxValueTolerance,  startPoint,  endPoint):
        #print inputRaster
        #print outputFile
        #print pointDistance
        #print maxValueTolerance
        
        rasterLayer = QgsMapLayerRegistry.instance().mapLayer( inputRaster )
        if rasterLayer is None:
            QMessageBox.critical( None,  QCoreApplication.translate( "ProfileExportPlugin", "Raster layer invalid"),  QCoreApplication.translate( "ProfileExportPlugin", "The selected raster layer could not be loaded") )
            return
            
        #test if start and endpoint are within the raster layer, bail out if not
        rasterExtent = rasterLayer.extent()
        if not rasterExtent.contains( startPoint ) or not rasterExtent.contains( endPoint ):
            QMessageBox.critical( None,  QCoreApplication.translate( "ProfileExportPlugin", "Error"),  QCoreApplication.translate( "ProfileExportPlugin", "Both endpoints need to be inside the raster extent") )
            return
          
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
        
        #debug only: write exported coordinates to csv file
        #debugFile = QFile( '/home/marco/tmp/debugfile.csv' )
        #debugFile.open( QIODevice.WriteOnly )
        #debugTextStream = QTextStream( debugFile )
        #debugNPoints = 0
        #debugTextStream.__lshift__("n,x,y,z").__lshift__("\n")
        
        dist = 0.0
        lastDist = 0.0
        currentValue = 0.0
        firstZ = self.firstRasterBandValue( startPoint ,  rasterLayer )
        lastValue = firstZ
        currentX = startPoint.x()
        currentY = startPoint.y()
        while dist < profileLength:
            currentValue = self.firstRasterBandValue( QgsPoint( currentX,  currentY ),  rasterLayer )
            
            #elevation tolerance between two points exceeded. Insert additional points
            if( currentValue - lastValue ) > maxValueTolerance: 
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
                    currentIntermediateValue = self.firstRasterBandValue( QgsPoint( xIntermediate,  yIntermediate ),  rasterLayer )
                    self.addElevationPoint( resultXmlDocument,  documentElement, dist - pointDistance + intermediateDist,  dIntermediatePointDist,    currentIntermediateValue - lastIntermediateValue,  currentIntermediateValue - firstZ,  xIntermediate, yIntermediate )
                    #debugTextStream.__lshift__(QString.number(debugNPoints)).__lshift__(",").__lshift__( QString.number(xIntermediate, 'f',  8) ).__lshift__(",").__lshift__( QString.number( yIntermediate, 'f', 8 ) ).__lshift__(",").__lshift__(QString.number( currentIntermediateValue, 'f', 8 ) ).__lshift__("\n")
                    #debugNPoints += 1
                    lastIntermediateValue = currentIntermediateValue
                    lastDist = dist - pointDistance + intermediateDist
            
            self.addElevationPoint( resultXmlDocument,  documentElement,  dist,  dist - lastDist,  currentValue - lastValue,  currentValue - firstZ,  currentX,  currentY )
            #debugTextStream.__lshift__(QString.number(debugNPoints)).__lshift__(",").__lshift__( QString.number(currentX, 'f', 8) ).__lshift__(",").__lshift__( QString.number( currentY, 'f', 8) ).__lshift__(",").__lshift__(QString.number( currentValue, 'f', 8 ) ).__lshift__("\n")
            #debugNPoints += 1
            currentX += dx
            currentY += dy
            lastDist = dist
            dist += pointDistance
            lastValue = currentValue
        
        #last value normally does not fit into the point interval
        if currentX != endPoint.x() or currentY != entPoint.y():
            currentValue = self.firstRasterBandValue( endPoint,  rasterLayer )
            self.addElevationPoint( resultXmlDocument,  documentElement,  profileLength,  pointDistance - ( dist - profileLength ), currentValue - lastValue,  currentValue - firstZ,  endPoint.x(),  endPoint.y()  )
            #debugTextStream.__lshift__(QString.number(debugNPoints)).__lshift__(",").__lshift__( QString.number(endPoint.x(), 'f', 8) ).__lshift__(",").__lshift__( QString.number( endPoint.y() , 'f', 8) ).__lshift__(",").__lshift__(QString.number( currentValue, 'f', 8 ) ).__lshift__("\n")
            
        #debugFile.close()
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
        distElemText = xmlDoc.createTextNode( QString.number( totDist ) )
        distElem.appendChild( distElemText)
        importGisElem.appendChild( distElem )
        #z0
        z0Elem = xmlDoc.createElement("z0")
        z0ElemText = xmlDoc.createTextNode( QString.number( z ) )
        z0Elem.appendChild( z0ElemText )
        importGisElem.appendChild( z0Elem )
        #entfernung
        entfElem = xmlDoc.createElement("entfernung")
        entfElemText = xmlDoc.createTextNode( QString.number( dist ) )
        entfElem.appendChild( entfElemText )
        importGisElem.appendChild( entfElem )
        #höhe
        hoeheElem = xmlDoc.createElement(u"höhe" )
        hoeheElemText = xmlDoc.createTextNode( QString.number( dz) )
        hoeheElem.appendChild( hoeheElemText )
        importGisElem.appendChild( hoeheElem )
        #koord_e
        koordEElem = xmlDoc.createElement("koord_e")
        koordEElemText = xmlDoc.createTextNode( QString.number(wgs_x, 'f', 8 ) )
        koordEElem.appendChild( koordEElemText)
        importGisElem.appendChild( koordEElem )
        #koord_n
        koordNElem = xmlDoc.createElement("koord_n")
        koordNElemText = xmlDoc.createTextNode( QString.number( wgs_y,  'f',  8 ) )
        koordNElem.appendChild( koordNElemText )
        importGisElem.appendChild( koordNElem )
        
        parentElement.appendChild( importGisElem )
        
    def firstRasterBandValue(self,  point,  rasterLayer):
        res,  ident = rasterLayer.identify( point )
        
        if len(ident) < 1:
            return -9999
        return ident[ ident.keys()[0] ].toDouble()[0]
