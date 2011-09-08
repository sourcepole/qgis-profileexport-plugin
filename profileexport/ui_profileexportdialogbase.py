# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'profileexportdialogbase.ui'
#
# Created: Mon Aug  8 11:37:41 2011
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ProfileExportDialogBase(object):
    def setupUi(self, ProfileExportDialogBase):
        ProfileExportDialogBase.setObjectName(_fromUtf8("ProfileExportDialogBase"))
        ProfileExportDialogBase.resize(389, 168)
        self.gridLayout = QtGui.QGridLayout(ProfileExportDialogBase)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.mPointDistanceLabel = QtGui.QLabel(ProfileExportDialogBase)
        self.mPointDistanceLabel.setObjectName(_fromUtf8("mPointDistanceLabel"))
        self.gridLayout.addWidget(self.mPointDistanceLabel, 0, 0, 1, 1)
        self.mPointDistanceSpinBox = QtGui.QDoubleSpinBox(ProfileExportDialogBase)
        self.mPointDistanceSpinBox.setObjectName(_fromUtf8("mPointDistanceSpinBox"))
        self.gridLayout.addWidget(self.mPointDistanceSpinBox, 0, 1, 1, 2)
        self.mMaximumElevationDifferenceLabel = QtGui.QLabel(ProfileExportDialogBase)
        self.mMaximumElevationDifferenceLabel.setObjectName(_fromUtf8("mMaximumElevationDifferenceLabel"))
        self.gridLayout.addWidget(self.mMaximumElevationDifferenceLabel, 1, 0, 1, 1)
        self.mMaxValueDifferenceSpinBox = QtGui.QDoubleSpinBox(ProfileExportDialogBase)
        self.mMaxValueDifferenceSpinBox.setObjectName(_fromUtf8("mMaxValueDifferenceSpinBox"))
        self.gridLayout.addWidget(self.mMaxValueDifferenceSpinBox, 1, 1, 1, 2)
        self.mRasterLayerComboBox = QtGui.QComboBox(ProfileExportDialogBase)
        self.mRasterLayerComboBox.setObjectName(_fromUtf8("mRasterLayerComboBox"))
        self.gridLayout.addWidget(self.mRasterLayerComboBox, 2, 1, 1, 2)
        self.mRasterLayerLabel = QtGui.QLabel(ProfileExportDialogBase)
        self.mRasterLayerLabel.setObjectName(_fromUtf8("mRasterLayerLabel"))
        self.gridLayout.addWidget(self.mRasterLayerLabel, 2, 0, 1, 1)
        self.mOutputFileLabel = QtGui.QLabel(ProfileExportDialogBase)
        self.mOutputFileLabel.setObjectName(_fromUtf8("mOutputFileLabel"))
        self.gridLayout.addWidget(self.mOutputFileLabel, 3, 0, 1, 1)
        self.mOutputFileLineEdit = QtGui.QLineEdit(ProfileExportDialogBase)
        self.mOutputFileLineEdit.setObjectName(_fromUtf8("mOutputFileLineEdit"))
        self.gridLayout.addWidget(self.mOutputFileLineEdit, 3, 1, 1, 1)
        self.mOutputFileToolButton = QtGui.QToolButton(ProfileExportDialogBase)
        self.mOutputFileToolButton.setObjectName(_fromUtf8("mOutputFileToolButton"))
        self.gridLayout.addWidget(self.mOutputFileToolButton, 3, 2, 1, 1)
        self.mButtonBox = QtGui.QDialogButtonBox(ProfileExportDialogBase)
        self.mButtonBox.setOrientation(QtCore.Qt.Horizontal)
        self.mButtonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.mButtonBox.setObjectName(_fromUtf8("mButtonBox"))
        self.gridLayout.addWidget(self.mButtonBox, 4, 0, 1, 1)

        self.retranslateUi(ProfileExportDialogBase)
        QtCore.QObject.connect(self.mButtonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ProfileExportDialogBase.accept)
        QtCore.QObject.connect(self.mButtonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ProfileExportDialogBase.reject)
        QtCore.QMetaObject.connectSlotsByName(ProfileExportDialogBase)

    def retranslateUi(self, ProfileExportDialogBase):
        ProfileExportDialogBase.setWindowTitle(QtGui.QApplication.translate("ProfileExportDialogBase", "Export selected profile", None, QtGui.QApplication.UnicodeUTF8))
        self.mPointDistanceLabel.setText(QtGui.QApplication.translate("ProfileExportDialogBase", "Point distance", None, QtGui.QApplication.UnicodeUTF8))
        self.mMaximumElevationDifferenceLabel.setText(QtGui.QApplication.translate("ProfileExportDialogBase", "Maximum value difference", None, QtGui.QApplication.UnicodeUTF8))
        self.mRasterLayerLabel.setText(QtGui.QApplication.translate("ProfileExportDialogBase", "Raster layer", None, QtGui.QApplication.UnicodeUTF8))
        self.mOutputFileLabel.setText(QtGui.QApplication.translate("ProfileExportDialogBase", "Output file", None, QtGui.QApplication.UnicodeUTF8))
        self.mOutputFileToolButton.setText(QtGui.QApplication.translate("ProfileExportDialogBase", "...", None, QtGui.QApplication.UnicodeUTF8))

