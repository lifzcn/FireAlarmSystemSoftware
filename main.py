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
import cv2
import numpy as np
from interface import Ui_Form
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtWidgets import QApplication, QMainWindow


class mainWindow(QMainWindow, Ui_Form):
    def __init__(self, parent=None):
        super(mainWindow, self).__init__(parent)
        self.setupUi(self)
        self.videoCapture = cv2.VideoCapture(0)
        self.createItems()
        self.createSignalSlot()

    def createItems(self):
        self.com = QSerialPort()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.showTime)
        self.timer.timeout.connect(self.updateVideo)
        self.timer.start(100)

    def createSignalSlot(self):
        self.pushButton_Open.clicked.connect(self.comOpen)
        self.pushButton_Close.clicked.connect(self.comClose)
        self.pushButton_Refresh.clicked.connect(self.comRefresh)
        self.com.readyRead.connect(self.receiveData)
        self.pushButton_SetTemperatureLimitValue.clicked.connect(self.setTemperatureLimitValue)
        self.pushButton_SetHumidityLimitValue.clicked.connect(self.setHumidityLimitValue)
        self.pushButton_SetSmokeLimitValue.clicked.connect(self.setSmokeLimitValue)
        self.pushButton_TemperatureAdjustConfirm.clicked.connect(self.transmitTemperatureAdjustValue)
        self.pushButton_HumidityAdjustConfirm.clicked.connect(self.transmitHumidityAdjustValue)
        self.pushButton_SmokeAdjustConfirm.clicked.connect(self.transmitSmokeAdjustValue)

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
            self.lineEdit_SmokeValue.setText(rxDataList[2] + "ppm")
        except Exception as e:
            QMessageBox.critical(self, "严重错误", "串口接收数据错误!\n" + str(e), None, None)

    def setTemperatureLimitValue(self):
        self.horizontalSlider_TemperatureAdjust.valueChanged.connect(self.updateTemperatureAdjustDisplay)

    def setHumidityLimitValue(self):
        self.horizontalSlider_HumidityAdjust.valueChanged.connect(self.updateHumidityAdjustDisplay)

    def setSmokeLimitValue(self):
        self.horizontalSlider_SmokeAdjust.valueChanged.connect(self.updateSmokeAdjustDisplay)

    def updateTemperatureAdjustDisplay(self, value):
        self.lineEdit_TemperatureAdjustDisplay.setText(str(value))

    def updateHumidityAdjustDisplay(self, value):
        self.lineEdit_HumidityAdjustDisplay.setText(str(value))

    def updateSmokeAdjustDisplay(self, value):
        self.lineEdit_SmokeAdjustDisplay.setText(str(value))

    def transmitTemperatureAdjustValue(self):
        txData = "T:" + self.lineEdit_TemperatureAdjustDisplay.text() + '\n'
        self.com.write(txData.encode("utf-8"))

    def transmitHumidityAdjustValue(self):
        txData = "H:" + self.lineEdit_HumidityAdjustDisplay.text() + '\n'
        self.com.write(txData.encode("utf-8"))

    def transmitSmokeAdjustValue(self):
        txData = "S:" + self.lineEdit_SmokeAdjustDisplay.text() + '\n'
        self.com.write(txData.encode("utf-8"))

    def updateVideo(self):
        ret, frame = self.videoCapture.read()
        if ret:
            rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgbImageTreated = self.fireRecognition(rgbImage)
            h, w, ch = rgbImageTreated.shape
            image = QImage(rgbImage.data, w, h, ch * w, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(image)
            self.label_videoCapture.setPixmap(pixmap)

    def closeEvent(self, event):
        self.videoCapture.release()
        event.accept()

    def fireRecognition(self, targetImg):
        img = targetImg
        redThre = 115
        sThre = 60
        B = img[:, :, 0]
        G = img[:, :, 1]
        R = img[:, :, 2]
        B1 = img[:, :, 0] / 255
        G1 = img[:, :, 1] / 255
        R1 = img[:, :, 2] / 255
        minValue = np.array(np.where(R1 <= G1, np.where(G1 <= B1, R1, np.where(R1 <= B1, R1, B1)), np.where(G1 <= B1, G1, B1)))
        sumValue = R1 + G1 + B1
        S = np.array(np.where(sumValue != 0, (1 - 3.0 * minValue / sumValue), 0))
        Sdet = (255 - R) / 20
        SThre = ((255 - R) * sThre / redThre)
        fireImg = np.array(np.where(R > redThre,
                                    np.where(R >= G,
                                    np.where(G >= B, np.where(S > 0,
                                    np.where(S > Sdet,
                                    np.where(S >= SThre, 255, 0), 0), 0), 0), 0), 0))
        gray_fireImg = np.zeros([fireImg.shape[0], fireImg.shape[1], 1], np.uint8)
        gray_fireImg[:, :, 0] = fireImg
        meBImg = cv2.medianBlur(gray_fireImg, 5)
        kernel = np.ones((5, 5), np.uint8)
        ProcImg = cv2.dilate(meBImg, kernel)
        contours, _ = cv2.findContours(ProcImg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        ResImg = img.copy()
        for c in range(0, len(contours)):
            x, y, w, h = cv2.boundingRect(contours[c])
            l_top = (x, y)
            r_bottom = (x + w, y + h)
            cv2.rectangle(ResImg, l_top, r_bottom, (255, 0, 0), 2)
        return ResImg

    def close(self):
        sys.exit(app.exec_())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWin = mainWindow()
    myWin.show()
    sys.exit(app.exec_())
