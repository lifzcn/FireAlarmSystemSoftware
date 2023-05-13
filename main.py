"""
# File       : main.py
# Encoding   : utf-8
# Date       ：2023/4/17
# Author     ：LiFZ
# Email      ：lifzcn@gmail.com
# Version    ：python 3.10
# Description：
"""

# 编码库
import re

# 系统库
import sys

# ascii转换库
import binascii

# Python时间库
import time

# 图片库
from PIL import Image

# PyQt5库
from PyQt5 import QtGui
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import *
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtWidgets import QApplication, QMainWindow

# 从界面初始化函数interface.py导入Ui_Form类
from interface import Ui_Form

# 条形码库
from barcode import EAN13

# 图片写入库
from barcode.writer import ImageWriter

# csv文件库
import csv


class mainWindow(QMainWindow, Ui_Form):
    def __init__(self, parent=None):  # 主函数初始化
        super(mainWindow, self).__init__(parent)
        self.setupUi(self)  # 设置UI界面
        self.createItems()  # 创造类型
        self.createSignalSlot()  # 创造函数槽

    def createItems(self):  # 创造类型子函数
        self.com = QSerialPort()  # 串口函数赋值
        self.timer = QTimer(self)  # 时间函数赋值
        self.timer.timeout.connect(self.showTime)  # 时间连接函数
        self.timer.timeout.connect(self.goodInfo)  # 商品信息连接函数
        self.timer.start(100)  # 时间开始函数

    def createSignalSlot(self):  # 创造函数槽
        self.pushButton_Open.clicked.connect(self.comOpen)  # 打开串口函数
        self.pushButton_Close.clicked.connect(self.comClose)  # 关闭串口函数
        self.pushButton_Refresh.clicked.connect(self.comRefresh)  # 刷新串口函数
        self.com.readyRead.connect(self.receiveData)  # 接收数据函数

    def showTime(self):  # 实时时间显示函数
        self.label_CurrentTime.setText(time.strftime("%B %d,%H:%M:%S", time.localtime()))

    def receiveData(self):  # 从串口接收数据函数
        try:
            rxData = bytes(self.com.readAll()).decode("utf-8")  # 读取串口数据并按照UTF-8进行解码
        except Exception as e:
            QMessageBox.critical(self, "严重错误", "串口接收数据错误!\n" + str(e))  # 如果接收信息出错，通过弹出框进行错误信息展示
        if not self.checkBox_HexShow.isChecked():  # 如果十六进制显示的复选框没有勾选
            try:
                standardizationWeight = round(float(rxData) / 1000, 2)  # 将接收到的数据除以1000，并保留两位小数
                self.lineEdit_Weight.setText(str(standardizationWeight) + " kg")  # 将得到的数据以kg的形式进行展示
                goodNameTemp = self.comboBox_Name.currentText()  # 从名称复选框中得到数据
                goodUnitPrice = float(self.findPriceInfo(goodNameTemp))  # 根据得到的商品名称进行单价的索引，返回值就是对应商品的单价
                goodPrice = round(standardizationWeight * goodUnitPrice, 2)  # 将总价保留两位小数
                self.lineEdit_Price.setText(str(goodPrice) + " 元")  # 以元为单位进行展示
            except:
                pass
        else:  # 如果十六进制显示的复选框已经勾选，则将数据以十六进制的形式进行展示
            data = binascii.b2a_hex(rxData).decode("ascii")
            hexStr = " 0x".join(re.findall("(.{2})", data))
            hexStr = "0x" + hexStr
            self.lineEdit_Weight.setText(hexStr)

    def comRefresh(self):  # 串口刷新函数
        self.comboBox_ComNo.clear()  # 将之前串口进行清除
        com = QSerialPort()  # 获取串口号
        com_list = QSerialPortInfo.availablePorts()  # 将已经存在的串口写入列表
        for info in com_list:  # 列表进行索引
            com.setPort(info)  # 将串口信息写入
            if com.open(QSerialPort.ReadWrite):  # 如果串口读写已打开
                self.comboBox_ComNo.addItem(info.portName())  # 将该串口引入
                com.close()  # 再进行关闭

    def hexShow(self):  # 十六进制显示函数
        if self.checkBox_HexShow.isChecked():  # 如果十六进制复选框已经勾选
            pass

    def comOpen(self):  # 串口打开函数
        comName = self.comboBox_ComNo.currentText()  # 从复选框获取当前想要打开的串口号
        comBaud = int(self.comboBox_Baud.currentText())  # 从波特率复选框获取要设置的波特率
        self.com.setPortName(comName)  # 根据获得的串口号设置串口
        try:
            if not self.com.open(QSerialPort.ReadWrite):
                QMessageBox.critical(self, "严重错误", "串口打开失败!")
                return
        except Exception as e:
            QMessageBox.critical(self, "严重错误", "串口打开失败!\n" + str(e))
            return
        self.pushButton_Close.setEnabled(True)
        self.pushButton_Open.setEnabled(False)
        self.pushButton_Refresh.setEnabled(False)
        self.comboBox_ComNo.setEnabled(False)
        self.comboBox_Baud.setEnabled(False)
        self.label_ComStatement.setText("已打开!")  # 串口状态显示
        self.com.setBaudRate(comBaud)  # 设置波特率

    def comClose(self):  # 串口关闭函数
        self.com.close()  # 直接当前软件使用的串口
        self.pushButton_Close.setEnabled(False)
        self.pushButton_Open.setEnabled(True)
        self.pushButton_Refresh.setEnabled(True)
        self.comboBox_ComNo.setEnabled(True)
        self.comboBox_Baud.setEnabled(True)
        self.label_ComStatement.setText("已关闭!")  # 串口状态显示

    def goodInfo(self):  # 商品信息函数
        goodName = self.comboBox_Name.currentText()  # 从商品名称复选框获取商品名称
        goodNumber = self.findNumberInfo(goodName)  # 根据名称得到编号
        self.lineEdit_Number.setText(goodNumber)  # 将编号进行展示
        goodBarcode = EAN13(goodNumber, writer=ImageWriter())  # 根据编号生成条形码数据
        goodBarcode.save("tempPic")  # 将条形码以图片形式进行存储
        adjustPic = Image.open("tempPic.png")  # 图片格式转换
        adjustPic = adjustPic.resize((400, 160))  # 图片大小调整
        adjustPic.save("tempPic.png")  # 将调整完之后的图片进行保存
        self.label_Barcode.setPixmap(QtGui.QPixmap("tempPic.png"))  # 通过Label控件将保存的图片进行展示

    def findNumberInfo(self, parameter):  # 获取商品编号信息
        with open("dataset.csv", mode='r', encoding="utf-8") as file:  # 打开数据集文件
            nameList = csv.DictReader(file)  # 直接形式打开
            for entry in nameList:  # 遍历整个文件
                if parameter == entry["Name"]:  # 匹配名称
                    return entry["Number"]  # 返回对应的编号

    def findPriceInfo(self, parameter):  # 获取商品单价信息
        with open("dataset.csv", mode='r', encoding="utf-8") as file:
            nameList = csv.DictReader(file)
            for entry in nameList:
                if parameter == entry["Name"]:
                    return entry["Price"]  # 返回对应的单价

    def close(self):  # 系统退出函数
        sys.exit(app.exec_())


if __name__ == "__main__":  # 主函数入口
    app = QApplication(sys.argv)
    myWin = mainWindow()
    myWin.show()
    sys.exit(app.exec_())
