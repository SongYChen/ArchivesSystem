# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'history_temp.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_history_temp(object):
    def setupUi(self, history_temp):
        history_temp.setObjectName("history_temp")
        history_temp.resize(351, 605)
        self.tableView = QtWidgets.QTableView(history_temp)
        self.tableView.setGeometry(QtCore.QRect(0, 40, 351, 501))
        self.tableView.setObjectName("tableView")
        self.horizontalLayoutWidget = QtWidgets.QWidget(history_temp)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(-1, 540, 351, 61))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.pushButton = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.horizontalLayoutWidget_2 = QtWidgets.QWidget(history_temp)
        self.horizontalLayoutWidget_2.setGeometry(QtCore.QRect(-1, 0, 351, 41))
        self.horizontalLayoutWidget_2.setObjectName("horizontalLayoutWidget_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_2)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem2)
        self.label = QtWidgets.QLabel(self.horizontalLayoutWidget_2)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem3)

        self.retranslateUi(history_temp)
        QtCore.QMetaObject.connectSlotsByName(history_temp)

    def retranslateUi(self, history_temp):
        _translate = QtCore.QCoreApplication.translate
        history_temp.setWindowTitle(_translate("history_temp", "历史温度"))
        self.pushButton.setText(_translate("history_temp", "退出"))
        self.label.setText(_translate("history_temp", "<html><head/><body><p><span style=\" font-size:12pt; font-weight:600;\">历史温度数据</span></p></body></html>"))
