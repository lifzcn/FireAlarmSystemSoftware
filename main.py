"""
# File       : main.py
# Encoding   : utf-8
# Date       ：2023/5/13
# Author     ：LiFZ
# Email      ：lifzcn@gmail.com
# Version    ：python 3.10
# Description：
"""

import sys
import time
from interface import Ui_Form
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import *
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtWidgets import QApplication, QMainWindow


class mainWindow(QMainWindow, Ui_Form):
    def __init__(self, parent=None):
        super(mainWindow, self).__init__(parent)
        self.setupUi(self)
        self.createItems()
        self.createSignalSlot()

    def createItems(self):
        self.com = QSerialPort()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.showTime)
        self.timer.start(100)

    def createSignalSlot(self):
        self.pushButton_Open.clicked.connect(self.comOpen)
        self.pushButton_Close.clicked.connect(self.comClose)
        self.pushButton_Refresh.clicked.connect(self.comRefresh)
        self.com.readyRead.connect(self.receiveData)
        self.pushButton_SetTemperatureLimitValue.clicked.connect(self.setTemperatureLimitValue)
        self.pushButton_SetHumidityLimitValue.clicked.connect(self.setHumidityLimitValue)
        self.pushButton_SetSmokeLimitValue.clicked.connect(self.setSmokeLimitValue)

    def showTime(self):
        self.label_DateAndTime.setText(time.strftime("%B %d,%H:%M:%S", time.localtime()))

    def comRefresh(self):
        self.comboBox_ComName.clear()
        com = QSerialPort()
        com_list = QSerialPortInfo.availablePorts()
        for info in com_list:
            com.setPort(info)
            if com.open(QSerialPort.ReadWrite):
                self.comboBox_ComName.addItem(info.portName())
                com.close()

    def comOpen(self):
        comName = self.comboBox_ComName.currentText()
        comBaud = int(self.comboBox_BaudRate.currentText())
        self.com.setPortName(comName)
        try:
            if not self.com.open(QSerialPort.ReadWrite):
                QMessageBox.critical(self, "严重错误", "串口打开失败!")
                return
        except Exception as e:
            QMessageBox.critical(self, "严重错误", "串口打开失败!\n" + str(e), None, None)
            return
        self.pushButton_Close.setEnabled(True)
        self.pushButton_Open.setEnabled(False)
        self.pushButton_Refresh.setEnabled(False)
        self.comboBox_ComName.setEnabled(False)
        self.comboBox_BaudRate.setEnabled(False)
        self.label_ComStatement.setText("已打开!")
        self.com.setBaudRate(comBaud)

    def comClose(self):
        self.com.close()
        self.pushButton_Close.setEnabled(False)
        self.pushButton_Open.setEnabled(True)
        self.pushButton_Refresh.setEnabled(True)
        self.comboBox_ComName.setEnabled(True)
        self.comboBox_BaudRate.setEnabled(True)
        self.label_ComStatement.setText("已关闭!")

    def receiveData(self):
        try:
            rxData = bytes(self.com.readAll()).decode("utf-8")
            rxDataList = rxData.split(',')
            self.lineEdit_TemperatureValue.setText(rxDataList[0] + " ℃")
            self.lineEdit_HumidityValue.setText(rxDataList[1] + " %")
        except Exception as e:
            QMessageBox.critical(self, "严重错误", "串口接收数据错误!\n" + str(e))

    def setTemperatureLimitValue(self):
        if self.radioButton_TemperatureAdjustHigh.isChecked():
            self.radioButton_TemperatureAdjustLow.setEnabled(False)
            setTemperatureHighValue = self.horizontalSlider_TemperatureAdjust.value()
            self.lineEdit_TemperatureAdjustDisplay.setText(setTemperatureHighValue)
        if self.radioButton_TemperatureAdjustLow.isChecked():
            self.radioButton_TemperatureAdjustHigh.setEnabled(False)
            setTemperatureLowValue = self.horizontalSlider_TemperatureAdjust.value()
            self.lineEdit_TemperatureAdjustDisplay.setText(setTemperatureLowValue)

    def setHumidityLimitValue(self):
        if self.radioButton_HumidityAdjustHigh.isChecked():
            self.radioButton_HumidityAdjustLow.setEnabled(False)
            setHumidityHighValue = self.horizontalSlider_HumidityAdjust.value()
            self.lineEdit_HumidityAdjustDisplay.setText(setHumidityHighValue)
        if self.radioButton_TemperatureAdjustLow.isChecked():
            self.radioButton_HumidityAdjustHigh.setEnabled(False)
            setHumidityLowValue = self.horizontalSlider_HumidityAdjust.value()
            self.lineEdit_HumidityAdjustDisplay.setText(setHumidityLowValue)

    def setSmokeLimitValue(self):
        pass

    def close(self):
        sys.exit(app.exec_())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWin = mainWindow()
    myWin.show()
    sys.exit(app.exec_())
