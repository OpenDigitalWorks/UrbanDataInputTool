# -*- coding: utf-8 -*-
"""
/***************************************************************************
 UrbanDataInputDockWidget
                                 A QGIS plugin
 Urban Data Input Tool for QGIS
                             -------------------
        begin                : 2016-06-03
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Abhimanyu Acharya/ Space Syntax Limited
        email                : a.acharya@spacesyntax.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

from PyQt4 import QtGui, uic
from PyQt4.QtCore import pyqtSignal

# Initialize Qt resources from file resources.py



import os.path
from . import utility_functions as uf
from qgis.core import *
from qgis.gui import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from CreateNew_dialog import CreatenewDialog
import processing



FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'urban_data_input_dockwidget_base.ui'))



class UrbanDataInputDockWidget(QtGui.QDockWidget, FORM_CLASS):

    closingPlugin = pyqtSignal()

    def __init__(self, iface, parent=None):
        """Constructor."""
        super(UrbanDataInputDockWidget, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        # define globals
        self.iface = iface
        self.canvas = self.iface.mapCanvas()

        self.dlg = CreatenewDialog()

        # set up GUI operation signals
        self.dlg.closePopUpButton.clicked.connect(self.closePopUp)
        self.pushButtonNewFile.clicked.connect(self.newFileDialog)
        self.dlg.createNewFileCheckBox.stateChanged.connect(self.updateLayers)
        self.startpushButton.clicked.connect(self.loadFrontageLayer)
        self.updateFacadeButton.clicked.connect(self.updateSelectedFrontageAttribute)
        self.updateIDPushButton.clicked.connect(self.pushID)
        self.iface.mapCanvas().selectionChanged.connect(self.addDataFields)
        self.iface.legendInterface().itemRemoved.connect(self.updateLayers)
        self.iface.legendInterface().itemAdded.connect(self.updateLayers)
        self.dlg.pushButtonNewFileDLG.clicked.connect(self.newFrontageLayer)
        self.dlg.pushButtonSelectLocation.clicked.connect(self.selectSaveLocation)
        self.iface.legendInterface().itemRemoved.connect(self.updateExistingLayers)
        self.iface.legendInterface().itemAdded.connect(self.updateExistingLayers)
        self.iface.projectRead.connect(self.updateExistingLayers)
        self.iface.newProjectCreated.connect(self.updateExistingLayers)
        self.iface.legendInterface().itemRemoved.connect(self.enablePushIDcombo)
        self.iface.legendInterface().itemAdded.connect(self.enablePushIDcombo)
        self.iface.projectRead.connect(self.enablePushIDcombo)
        self.iface.newProjectCreated.connect(self.enablePushIDcombo)
        self.pushIDcomboBox.currentIndexChanged.connect(self.updatepushWidgetList)
        self.hideshowButton.clicked.connect(self.hideFeatures)

        # initialisation
        self.updateFrontageTypes()
        self.updateExistingLayers()
        self.updateLayersPushID()




        # add button icons

        #initial button state



        # override setting
        QSettings().setValue('/qgis/digitizing/disable_enter_attribute_values_dialog', True)
        QSettings().setValue('/qgis/crs/enable_use_project_crs', True)

    def closeEvent(self, event):
        # disconnect interface signals
        try:
            self.iface.projectRead.disconnect(self.updateLayers)
            self.iface.newProjectCreated.disconnect(self.updateLayers)
            self.iface.legendInterface().itemRemoved.disconnect(self.updateLayers)
            self.iface.legendInterface().itemAdded.disconnect(self.updateLayers)
            self.iface.projectRead.disconnect(self.updateFrontageTypes)
            self.iface.newProjectCreated.disconnect(self.updateFrontageTypes)
            self.iface.projectRead.disconnect(self.updateExistingLayers)
            self.iface.newProjectCreated.disconnect(self.updateExistingLayers)
            self.iface.legendInterface().itemRemoved.disconnect(self.updateExistingLayers)
            self.iface.legendInterface().itemAdded.disconnect(self.updateExistingLayers)
            self.iface.legendInterface().itemRemoved.disconnect(self.enablePushIDcombo)
            self.iface.legendInterface().itemAdded.disconnect(self.enablePushIDcombo)
            self.iface.projectRead.disconnect(self.enablePushIDcombo)
            self.iface.newProjectCreated.disconnect(self.enablePushIDcombo)



        except:
            pass

        self.closingPlugin.emit()
        event.accept()


    #######
    #   Data functions
    #######

    def closePopUp(self):
        self.dlg.close()


    def getSelectedLayer(self):
        layer_name = self.dlg.selectLUCombo.currentText()
        layer = uf.getLegendLayerByName(self.iface, layer_name)
        return layer

    def selectSaveLocation(self):
        filename = QFileDialog.getExistingDirectory(self.dlg, "Select Folder ", '')
        self.dlg.lineEditFrontages.setText(filename)

    def newFileDialog(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            self.dlg.lineEditFileName.clear()
            pass

    def updateLayers(self):
        self.dlg.selectLUCombo.clear()
        layers = self.iface.legendInterface().layers()
        layer_list = []

        if self.dlg.createNewFileCheckBox.checkState() == 2:

            for layer in layers:
                if layer.type() == QgsMapLayer.VectorLayer and layer.geometryType() == QGis.Polygon:
                    layer_list.append(layer.name())
                    self.dlg.selectLUCombo.setEditable(True)

            self.dlg.selectLUCombo.addItems(layer_list)


    def updateLayersPushID(self):
        self.pushIDcomboBox.clear()
        layers = self.iface.legendInterface().layers()
        layer_list = []

        for layer in layers:
            if layer.type() == QgsMapLayer.VectorLayer and layer.geometryType() == QGis.Polygon:
                self.pushIDcomboBox.setEditable(True)
                layer_list.append(layer.name())

        self.pushIDcomboBox.addItems(layer_list)

    def enablePushIDcombo(self):
        layers = self.iface.legendInterface().layers()

        if self.useExistingcomboBox.isEditable() == True:
            for layer in layers:
                if layer.type() == QgsMapLayer.VectorLayer and layer.geometryType() == QGis.Polygon:
                    self.pushIDcomboBox.setEditable(True)
                    self.updateLayersPushID()

        elif self.useExistingcomboBox.isEditable() == False:
            self.pushIDcomboBox.clear()
            self.pushIDcomboBox.setEditable(False)




    def updateFrontageTypes(self):
        self.frontageslistWidget.clear()
        frontage_list = []

        if self.useExistingcomboBox.isEditable() == True:

            frontage_list = ['Transparent', 'Semi Transparent', 'Blank',
                          'High Opaque Fence', 'High See Through Fence',
                          'Low Fence']

        self.frontageslistWidget.addItems(frontage_list)


    def getSelectedLayerLoad(self):
        layer_name = self.useExistingcomboBox.currentText()
        layer1 = uf.getLegendLayerByName(self.iface, layer_name)
        return layer1

    def getSelectedLayerPushID(self):
        layer_name = self.pushIDcomboBox.currentText()
        layer = uf.getLegendLayerByName(self.iface, layer_name)
        return layer

    def addDataFields(self):
        self.tableClear()
        filename = self.useExistingcomboBox.currentText()
        layer = None
        for lyr in self.iface.legendInterface().layers():
            if lyr.name() == filename:
                layer = lyr
                break

        if layer:
            features = layer.selectedFeatures()
            attrs = []
            for feat in features:
                attr = feat.attributes()
                attrs.append(attr)

            fields = layer.pendingFields()
            field_names = [field.name() for field in fields]

            field_length = len(field_names)
            A1 = field_length - 4
            A2 = field_length - 3
            A3 = field_length - 2

            self.tableWidgetFrontage.setColumnCount(3)
            headers = ["F-ID","Group","Type"]
            self.tableWidgetFrontage.setHorizontalHeaderLabels(headers)
            self.tableWidgetFrontage.setRowCount(len(attrs))

            for i, item in enumerate(attrs):
                self.tableWidgetFrontage.setItem(i, 0, QtGui.QTableWidgetItem(str(item[A1])))
                self.tableWidgetFrontage.setItem(i, 1, QtGui.QTableWidgetItem(str(item[A2])))
                self.tableWidgetFrontage.setItem(i, 2, QtGui.QTableWidgetItem(str(item[A3])))

            self.tableWidgetFrontage.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
            self.tableWidgetFrontage.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.ResizeToContents)
            self.tableWidgetFrontage.horizontalHeader().setResizeMode(2, QtGui.QHeaderView.Stretch)
            self.tableWidgetFrontage.resizeRowsToContents()

    def tableClear(self):
        self.tableWidgetFrontage.clear()


    def updateExistingLayers(self):
        self.useExistingcomboBox.clear()
        layers = self.iface.legendInterface().layers()
        layer_list = []

        for layer in layers:
            if layer.type() == QgsMapLayer.VectorLayer and layer.geometryType() == QGis.Line:
                layer_list.append(layer.name())
                self.useExistingcomboBox.setEditable(True)

            else:
                self.useExistingcomboBox.setEditable(False)

        self.useExistingcomboBox.addItems(layer_list)


        #######
        #   Frontages
        #######
    def newFrontageLayer(self):

        filename = self.dlg.lineEditFileName.text()
        format = ".shp"
        if self.dlg.createNewFileCheckBox.checkState() == 0:

            if self.dlg.lineEditFrontages.text() != "":
                destCRS = self.canvas.mapRenderer().destinationCrs()
                vl = QgsVectorLayer("LineString?crs=" + destCRS.toWkt(), "memory:Frontages", "memory")
                QgsMapLayerRegistry.instance().addMapLayer(vl)

                input1 = self.iface.activeLayer()
                location = self.dlg.lineEditFrontages.text() + filename + format
                QgsVectorFileWriter.writeAsVectorFormat(input1, location, "CP1250", None, "ESRI Shapefile")

                removelayer = QgsMapLayerRegistry.instance().mapLayersByName("memory:Frontages")[0]
                QgsMapLayerRegistry.instance().removeMapLayers([removelayer.id()])

                input2 = self.iface.addVectorLayer(location, filename, "ogr")

                if not input2:
                    msgBar = self.iface.messageBar()
                    msg = msgBar.createMessage(u'Layer failed to load!' + location)
                    msgBar.pushWidget(msg, QgsMessageBar.INFO, 10)

                else:
                    msgBar = self.iface.messageBar()
                    msg = msgBar.createMessage(u'Layer loaded:' + location)
                    msgBar.pushWidget(msg, QgsMessageBar.INFO, 10)

                input2.startEditing()

                edit1 = input2.dataProvider()
                edit1.addAttributes([QgsField("F_ID", QVariant.Int),
                                         QgsField("Group", QVariant.String),
                                         QgsField("Type", QVariant.String),
                                         QgsField("Length", QVariant.Double)])

                input2.commitChanges()
                input2.startEditing()
                self.dlg.lineEditFrontages.clear()

                plugin_path = os.path.dirname(__file__)
                qml_path = plugin_path + "/frontagesThematic.qml"
                input2.loadNamedStyle(qml_path)

                input2.featureAdded.connect(self.logFeatureAdded)
                input2.selectionChanged.connect(self.addDataFields)
                self.dlg.close()


            else:
                destCRS = self.canvas.mapRenderer().destinationCrs()
                vl = QgsVectorLayer("LineString?crs=" + destCRS.toWkt(), filename, "memory")
                QgsMapLayerRegistry.instance().addMapLayer(vl)

                layer = None
                for lyr in QgsMapLayerRegistry.instance().mapLayers().values():
                    if lyr.name() == filename:
                        layer = lyr
                        break

                input1 = layer

                edit1 = input1.dataProvider()
                edit1.addAttributes([QgsField("F_ID", QVariant.Int),
                                         QgsField("Group", QVariant.String),
                                         QgsField("Type", QVariant.String),
                                         QgsField("Length", QVariant.Double)])

                input1.commitChanges()
                input1.startEditing()

                plugin_path = os.path.dirname(__file__)
                qml_path = plugin_path + "/frontagesThematic.qml"
                input1.loadNamedStyle(qml_path)

                msgBar = self.iface.messageBar()
                msg = msgBar.createMessage(u'New Frontages Layer Created')
                msgBar.pushWidget(msg, QgsMessageBar.INFO, 5)

                input1.featureAdded.connect(self.logFeatureAdded)
                input1.selectionChanged.connect(self.addDataFields)
                self.dlg.close()


        elif self.dlg.createNewFileCheckBox.checkState() == 2:
            if self.dlg.lineEditFrontages.text() != "":
                input1 = self.getSelectedLayer()
                destCRS = input1.crs()
                processing.runandload("qgis:polygonstolines", input1, "Lines from polygons")
                input2 = self.iface.activeLayer()
                processing.runandload("qgis:explodelines", input2, "Exploded")

                layer = None
                for lyr in QgsMapLayerRegistry.instance().mapLayers().values():
                    if lyr.name() == "Exploded":
                        layer = lyr
                        break

                input3 = layer
                location = self.dlg.lineEditFrontages.text() + filename + format
                QgsVectorFileWriter.writeAsVectorFormat(input3, location, "System", None, "ESRI Shapefile")

                removelayer = QgsMapLayerRegistry.instance().mapLayersByName("Lines from polygons")[0]
                QgsMapLayerRegistry.instance().removeMapLayers([removelayer.id()])
                removelayer = QgsMapLayerRegistry.instance().mapLayersByName("Exploded")[0]
                QgsMapLayerRegistry.instance().removeMapLayers([removelayer.id()])

                input4 = self.iface.addVectorLayer(location, filename, "ogr")


                if not input4:
                    msgBar = self.iface.messageBar()
                    msg = msgBar.createMessage(u'Layer failed to load!' + location)
                    msgBar.pushWidget(msg, QgsMessageBar.INFO, 10)

                else:
                    msgBar = self.iface.messageBar()
                    msg = msgBar.createMessage(u'Layer loaded:' + location)
                    msgBar.pushWidget(msg, QgsMessageBar.INFO, 10)

                input4.startEditing()

                edit1 = input4.dataProvider()
                edit1.addAttributes([QgsField("F_ID", QVariant.Int),
                                         QgsField("Group", QVariant.String),
                                         QgsField("Type", QVariant.String),
                                         QgsField("Length", QVariant.Double)])

                input4.commitChanges()
                input4.startEditing()

                features = input4.getFeatures()
                i = 0
                for feat in features:
                    feat['F_ID'] = i
                    i += 1
                    input4.updateFeature(feat)

                    self.dlg.lineEditFrontages.clear()

                plugin_path = os.path.dirname(__file__)
                qml_path = plugin_path + "/frontagesThematic.qml"
                input4.loadNamedStyle(qml_path)

                input4.featureAdded.connect(self.logFeatureAdded)
                input4.selectionChanged.connect(self.addDataFields)
                self.dlg.close()


            else:
                input1 = self.getSelectedLayer()
                destCRS = input1.crs()
                processing.runandload("qgis:polygonstolines", input1, "Lines from polygons")
                input2 = self.iface.activeLayer()
                processing.runandload("qgis:explodelines", input2, "Exploded")

                removelayer = QgsMapLayerRegistry.instance().mapLayersByName("Lines from polygons")[0]
                QgsMapLayerRegistry.instance().removeMapLayers([removelayer.id()])

                layer = None
                for lyr in QgsMapLayerRegistry.instance().mapLayers().values():
                    if lyr.name() == "Exploded":
                        layer = lyr
                        break

                layer.setLayerName(filename)

                input3 = layer

                edit1 = input3.dataProvider()
                edit1.addAttributes([QgsField("F_ID", QVariant.Int),
                                         QgsField("Group", QVariant.String),
                                         QgsField("Type", QVariant.String),
                                         QgsField("Length", QVariant.Double)])

                input3.commitChanges()
                input3.startEditing()

                features = input3.getFeatures()
                i = 0
                for feat in features:
                    feat['F_ID'] = i
                    i += 1
                    input3.updateFeature(feat)

                plugin_path = os.path.dirname(__file__)
                qml_path = plugin_path + "/frontagesThematic.qml"
                input3.loadNamedStyle(qml_path)

                msgBar = self.iface.messageBar()
                msg = msgBar.createMessage(u'New Frontages Layer Created')
                msgBar.pushWidget(msg, QgsMessageBar.INFO, 5)

                input3.featureAdded.connect(self.logFeatureAdded)
                input3.selectionChanged.connect(self.addDataFields)
                self.dlg.close()


    # Load File

    def loadFrontageLayer(self):
        input = self.getSelectedLayerLoad()

        input.setLayerName("Frontages")

        input.startEditing()

        plugin_path = os.path.dirname(__file__)
        qml_path = plugin_path + "/frontagesThematic.qml"
        input.loadNamedStyle(qml_path)


        # Draw/Update Feature
    def logFeatureAdded(self, fid):
        QgsMessageLog.logMessage("feature added, id = " + str(fid))

        mc = self.canvas
        layer = None
        for lyr in QgsMapLayerRegistry.instance().mapLayers().values():
            if lyr.name() == "memory:Frontages" or lyr.name() == 'Frontages' :
                layer = lyr
                break

        v_layer = layer
        features = v_layer.getFeatures()
        i = 0
        for feat in features:
            feat['F_ID'] = i
            i += 1
            v_layer.updateFeature(feat)

        data = v_layer.dataProvider()

        update1 = data.fieldNameIndex("Group")
        update2 = data.fieldNameIndex("Type")
        update3 = data.fieldNameIndex("F_ID")
        self.updateLength()

        if self.frontageslistWidget.currentRow() == 0:
            v_layer.changeAttributeValue(fid, update1, "Building", True)
            v_layer.changeAttributeValue(fid, update2, "Transparent", True)

        if self.frontageslistWidget.currentRow() == 1:
            v_layer.changeAttributeValue(fid, update1, "Building", True)
            v_layer.changeAttributeValue(fid, update2, "Semi Transparent", True)

        if self.frontageslistWidget.currentRow() == 2:
            v_layer.changeAttributeValue(fid, update1, "Building", True)
            v_layer.changeAttributeValue(fid, update2, "Blank", True)

        if self.frontageslistWidget.currentRow() == 3:
            v_layer.changeAttributeValue(fid, update1, "Fence", True)
            v_layer.changeAttributeValue(fid, update2, "High Opaque Fence", True)

        if self.frontageslistWidget.currentRow() == 4:
            v_layer.changeAttributeValue(fid, update1, "Fence", True)
            v_layer.changeAttributeValue(fid, update2, "High See Through Fence", True)

        if self.frontageslistWidget.currentRow() == 5:
            v_layer.changeAttributeValue(fid, update1, "Fence", True)
            v_layer.changeAttributeValue(fid, update2, "Low Fence", True)
            
    def updateLength(self):
        mc = self.canvas
        layer = None
        for lyr in QgsMapLayerRegistry.instance().mapLayers().values():
            if lyr.name() == "memory:Frontages" or lyr.name() == 'Frontages':
                layer = lyr
                break

        v_layer = layer
        features = v_layer.getFeatures()

        for feat in features:
            geom = feat.geometry()
            feat['Length'] = geom.length()
            v_layer.updateFeature(feat)

    def updateSelectedFrontageAttribute(self):
        QApplication.beep()
        mc = self.canvas
        layer = None
        for lyr in QgsMapLayerRegistry.instance().mapLayers().values():
            if lyr.name() == "memory:Frontages" or lyr.name() == 'Frontages':
                layer = lyr
                break

        features = layer.selectedFeatures()

        if self.frontageslistWidget.currentRow() == 0:
            for feat in features:
                feat['Group'] = "Building"
                feat['Type'] = "Transparent"
                geom = feat.geometry()
                feat['Length'] = geom.length()
                layer.updateFeature(feat)
                self.addDataFields()

        if self.frontageslistWidget.currentRow() == 1:
            for feat in features:
                feat['Group'] = "Building"
                feat['Type'] = "Semi Transparent"
                geom = feat.geometry()
                feat['Length'] = geom.length()
                layer.updateFeature(feat)
                self.addDataFields()

        if self.frontageslistWidget.currentRow() == 2:
            for feat in features:
                feat['Group'] = "Building"
                feat['Type'] = "Blank"
                geom = feat.geometry()
                feat['Length'] = geom.length()
                layer.updateFeature(feat)
                self.addDataFields()

        if self.frontageslistWidget.currentRow() == 3:
            for feat in features:
                feat['Group'] = "Fence"
                feat['Type'] = "High Opaque Fence"
                geom = feat.geometry()
                feat['Length'] = geom.length()
                layer.updateFeature(feat)
                self.addDataFields()

        if self.frontageslistWidget.currentRow() == 4:
            for feat in features:
                feat['Group'] = "Fence"
                feat['Type'] = "High See Through Fence"
                geom = feat.geometry()
                feat['Length'] = geom.length()
                layer.updateFeature(feat)
                self.addDataFields()

        if self.frontageslistWidget.currentRow() == 5:
            for feat in features:
                feat['Group'] = "Fence"
                feat['Type'] = "Low Fence"
                geom = feat.geometry()
                feat['Length'] = geom.length()
                layer.updateFeature(feat)
                self.addDataFields()



    def hideFeatures(self):
        mc = self.canvas
        layer = None
        for lyr in QgsMapLayerRegistry.instance().mapLayers().values():
            if lyr.name() == "memory:Frontages" or lyr.name() == 'Frontages':
                layer = lyr
                break

        if self.hideshowButton.isChecked():
            plugin_path = os.path.dirname(__file__)
            qml_path = plugin_path + "/frontagesThematic_NULL.qml"
            layer.loadNamedStyle(qml_path)
            mc.refresh()

        else:
            plugin_path = os.path.dirname(__file__)
            qml_path = plugin_path + "/frontagesThematic.qml"
            layer.loadNamedStyle(qml_path)
            mc.refresh()


    def updatepushWidgetList(self):
        if self.pushIDcomboBox.isEditable()== True:
            self.pushIDlistWidget.clear()
            buildinglayer = self.getSelectedLayerPushID()
            if buildinglayer:
                features = buildinglayer.getFeatures()
                attrs = []
                for feat in features:
                    attr = feat.attributes()
                    attrs.append(attr)

                fields = buildinglayer.pendingFields()
                field_names = [field.name() for field in fields]
                self.pushIDlistWidget.addItems(field_names)

        elif self.pushIDcomboBox.isEditable()== False:
            self.pushIDlistWidget.clear()


    def pushID(self):
        buildinglayer = self.getSelectedLayerPushID()

        mc = self.canvas
        frontlayer = None
        for lyr in QgsMapLayerRegistry.instance().mapLayers().values():
            if lyr.name() == "memory:Frontages" or lyr.name() == 'Frontages':
                frontlayer = lyr
                break

        frontlayer.startEditing()

        buildingID = self.pushIDlistWidget.currentItem().text()
        print buildingID
        newColumn = "Building_" + buildingID
        frontlayer_pr = frontlayer.dataProvider()
        frontlayer_pr.addAttributes([QgsField( newColumn, QVariant.Int)])
        frontlayer.commitChanges()
        frontlayer.startEditing()
        frontlayer_caps = frontlayer_pr.capabilities()

        for buildfeat in buildinglayer.getFeatures():
            for frontfeat in frontlayer.getFeatures():
                if frontfeat.geometry().intersects(buildfeat.geometry()) == True:
                    frontlayer.startEditing()

                    if frontlayer_caps & QgsVectorDataProvider.ChangeAttributeValues:
                        frontfeat[newColumn] = buildfeat[buildingID]
                        frontlayer.updateFeature(frontfeat)
                        frontlayer.commitChanges()
























