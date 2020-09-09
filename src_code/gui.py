from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread, Qt, pyqtSignal
from PyQt5.QtGui import QPalette, QBrush, QPixmap
from route import *
from travel_state_page_generate import *
from time_table import *
from travle_log import *
import threading
import datetime
import sys
import os

# 初始时间
init_time = datetime.datetime(2020, 5, 7, 0)
city_id = {'北京': {"transportation": [], "id": 0}, '上海': {"transportation": [], "id": 1},
             '广州': {"transportation": [], "id": 2},
             '哈尔滨': {"transportation": [], "id": 3},
             '沈阳': {"transportation": [], "id": 4}, '天津': {"transportation": [], "id": 5},
             '兰州': {"transportation": [], "id": 6},
             '成都': {"transportation": [], "id": 7},
             '贵阳': {"transportation": [], "id": 8}, '武汉': {"transportation": [], "id": 9},
             '海口': {"transportation": [], "id": 10},
             '乌鲁木齐': {"transportation": [], "id": 11}}
# 多少秒增加1h
time_gap = 5

# 主页面
class Ui_MainWindow(QWidget):
    open_map_signal = pyqtSignal(dict)

    # 初始化信号和槽
    def initSlot(self):
        self.time_thread.time_update_signal.connect(self.time_update)
        self.time_thread.get_route_signal.connect(self.get_route)
        self.pushButton.clicked.connect(self.mp.show)
        self.pushButton_3.clicked.connect(self.get_mission)
        self.stop_timer_btn.clicked.connect(self.time_thread.stop_timer)
        self.stop_timer_btn.clicked.connect(self.stop_timer)
        self.start_timer_btn.clicked.connect(self.time_thread.start_timer)
        self.start_timer_btn.clicked.connect(self.start_timer)
        self.comboBox_3.currentIndexChanged.connect(self.change_dep_combo)

        # 用户操作任务时，停止计时
        self.comboBox_3.currentIndexChanged.connect(self.time_thread.stop_timer)
        self.comboBox_3.currentIndexChanged.connect(self.stop_timer)
        self.comboBox_2.currentIndexChanged.connect(self.time_thread.stop_timer)
        self.comboBox_2.currentIndexChanged.connect(self.stop_timer)
        # self.comboBox.currentIndexChanged.connect(self.time_thread.stop_timer)
        # self.comboBox.currentIndexChanged.connect(self.stop_timer)
        self.checkBox.toggled.connect(self.time_thread.stop_timer)
        self.checkBox.toggled.connect(self.stop_timer)
        self.limit_time_input.valueChanged.connect(self.time_thread.stop_timer)
        self.limit_time_input.valueChanged.connect(self.stop_timer)

        # 用户打开地图时，停止计时
        # self.pushButton.clicked.connect(self.time_thread.stop_timer)
        # self.pushButton.clicked.connect(self.stop_timer)
        self.pushButton.clicked.connect(self.open_map)

        # 用户提交任务后，自动开始计时
        self.pushButton_3.clicked.connect(self.time_thread.start_timer)
        self.pushButton_3.clicked.connect(self.start_timer)

    def __init__(self):
        super(Ui_MainWindow,self).__init__()
        # 初始化
        self.city_graph = get_city_graph()
        self.schedule = get_schedule()
        # 六个旅客
        self.traveller_list = []
        for i in range(6):
            self.traveller_list.append(
                {'id': i, "departure": '', "destination": "", "route": [], "in_trans": 0,
                 "route_index": 0, "time_limit": 0,"arrived":1,"present_city":""})

        self.map_on = False

        self.log = open("travel_log.txt","w+",encoding='utf-8')

    def __del__(self):
        self.log.close()

    def stop_timer(self):
        self.timer_status.setText("时间状态：暂停")

    def start_timer(self):
        self.timer_status.setText("时间状态：正常")

    # 初始化
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1000, 500)
        MainWindow.setWindowTitle("Covid-19旅行模拟系统")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.mission_info = QtWidgets.QFrame(self.centralwidget)
        self.mission_info.setGeometry(QtCore.QRect(40, 20, 301, 191))
        self.mission_info.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.mission_info.setFrameShadow(QtWidgets.QFrame.Raised)
        self.mission_info.setObjectName("mission_info")
        self.label = QtWidgets.QLabel(self.mission_info)
        self.label.setGeometry(QtCore.QRect(0, 0, 81, 31))
        self.label.setObjectName("label")
        self.label_3 = QtWidgets.QLabel(self.mission_info)
        self.label_3.setGeometry(QtCore.QRect(30, 30, 241, 21))
        self.label_3.setObjectName("label_3")
        self.widget = QtWidgets.QWidget(self.mission_info)
        self.widget.setGeometry(QtCore.QRect(10, 70, 281, 121))
        self.widget.setObjectName("widget")
        self.gridLayout = QtWidgets.QGridLayout(self.widget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.timer_status = QtWidgets.QLabel(self.mission_info)
        self.timer_status.setGeometry(QtCore.QRect(30, 50, 131, 31))
        self.timer_status.setObjectName("timer_status")
        self.stop_timer_btn = QtWidgets.QPushButton(self.widget)
        self.stop_timer_btn.setObjectName("stop_timer_btn")
        self.gridLayout.addWidget(self.stop_timer_btn, 0, 0, 1, 1)
        self.start_timer_btn = QtWidgets.QPushButton(self.widget)
        self.start_timer_btn.setObjectName("start_timer_btn")
        self.gridLayout.addWidget(self.start_timer_btn, 0, 1, 1, 1)
        self.pushButton = QtWidgets.QPushButton(self.widget)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 1, 0, 1, 1)
        self.pushButton_2 = QtWidgets.QPushButton(self.widget)
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout.addWidget(self.pushButton_2, 1, 1, 1, 1)
        self.mission_input = QtWidgets.QFrame(self.centralwidget)
        self.mission_input.setGeometry(QtCore.QRect(40, 220, 301, 281))
        self.mission_input.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.mission_input.setFrameShadow(QtWidgets.QFrame.Raised)
        self.mission_input.setObjectName("mission_input")
        self.label_2 = QtWidgets.QLabel(self.mission_input)
        self.label_2.setGeometry(QtCore.QRect(12, 12, 75, 16))
        self.label_2.setObjectName("label_2")
        self.layoutWidget = QtWidgets.QWidget(self.mission_input)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 80, 271, 55))
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_5 = QtWidgets.QLabel(self.layoutWidget)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_3.addWidget(self.label_5)
        self.comboBox = QtWidgets.QComboBox(self.layoutWidget)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.horizontalLayout_3.addWidget(self.comboBox)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_6 = QtWidgets.QLabel(self.layoutWidget)
        self.label_6.setObjectName("label_6")
        self.horizontalLayout.addWidget(self.label_6)
        self.comboBox_2 = QtWidgets.QComboBox(self.layoutWidget)
        self.comboBox_2.setObjectName("comboBox_2")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.horizontalLayout.addWidget(self.comboBox_2)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.layoutWidget1 = QtWidgets.QWidget(self.mission_input)
        self.layoutWidget1.setGeometry(QtCore.QRect(10, 140, 271, 88))
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.layoutWidget1)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_7 = QtWidgets.QLabel(self.layoutWidget1)
        self.label_7.setObjectName("label_7")
        self.horizontalLayout_2.addWidget(self.label_7)
        self.checkBox_3 = QtWidgets.QCheckBox(self.layoutWidget1)
        self.checkBox_3.setChecked(True)
        self.checkBox_3.setObjectName("checkBox_3")
        self.horizontalLayout_2.addWidget(self.checkBox_3)
        self.checkBox = QtWidgets.QCheckBox(self.layoutWidget1)
        self.checkBox.setObjectName("checkBox")
        self.horizontalLayout_2.addWidget(self.checkBox)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_8 = QtWidgets.QLabel(self.layoutWidget1)
        self.label_8.setObjectName("label_8")
        self.horizontalLayout_4.addWidget(self.label_8)
        self.limit_time_input = QtWidgets.QSpinBox(self.layoutWidget1)
        self.limit_time_input.setWrapping(False)
        self.limit_time_input.setObjectName("limit_time_input")
        self.horizontalLayout_4.addWidget(self.limit_time_input)
        self.verticalLayout_2.addLayout(self.horizontalLayout_4)
        self.pushButton_3 = QtWidgets.QPushButton(self.layoutWidget1)
        self.pushButton_3.setObjectName("pushButton_3")
        self.verticalLayout_2.addWidget(self.pushButton_3)
        self.label_4 = QtWidgets.QLabel(self.mission_input)
        self.label_4.setGeometry(QtCore.QRect(10, 50, 75, 16))
        self.label_4.setObjectName("label_4")
        self.comboBox_3 = QtWidgets.QComboBox(self.mission_input)
        self.comboBox_3.setGeometry(QtCore.QRect(150, 50, 130, 21))
        self.comboBox_3.setObjectName("comboBox_3")
        self.comboBox_3.addItem("")
        self.comboBox_3.addItem("")
        self.comboBox_3.addItem("")
        self.comboBox_3.addItem("")
        self.comboBox_3.addItem("")
        self.comboBox_3.addItem("")
        self.textBrowser_2 = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser_2.setGeometry(QtCore.QRect(380, 20, 581, 441))
        self.textBrowser_2.setObjectName("textBrowser_2")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.checkBox_3.clicked.connect(self.checkBox.toggle)
        self.checkBox.clicked.connect(self.checkBox_3.toggle)
        self.pushButton_2.clicked.connect(MainWindow.close)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # 控制文字大小
        self.label.setStyleSheet('''
            QLabel{
                font:20px/1 Tahoma,Helvetica,Arial,"\5b8b\4f53",sans-serif;
            }
        ''')
        self.label_2.setStyleSheet('''
            QLabel{
                font:18px/1 Tahoma,Helvetica,Arial,"\5b8b\4f53",sans-serif;
            }
        ''')

        # 让按钮保持按下
        self.pushButton.setCheckable(True)
        self.pushButton.setAutoExclusive(True)
        self.pushButton_2.setCheckable(True)
        self.pushButton_2.setAutoExclusive(True)
        self.start_timer_btn.setCheckable(True)
        self.start_timer_btn.setAutoExclusive(True)
        self.stop_timer_btn.setCheckable(True)
        self.stop_timer_btn.setAutoExclusive(True)

        # 设置限制时间值域
        self.limit_time_input.setRange(0, 9999)

        # 设置地图页面
        self.mp = QDialog()
        self.map = Ui_Dialog()
        self.map.setupUi(self.mp)

        # 时间线程
        self.time_thread = TimeThread()
        self.time_thread.start()

        # 设置信号和槽
        self.initSlot()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Covid-19旅行模拟系统"))
        #MainWindow.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        #MainWindow.setWindowOpacity(0.9)  # 设置窗口透明度
        #MainWindow.setAttribute(QtCore.Qt.WA_TranslucentBackground)  # 设置窗口背景透明


        # 背景颜色
        pe = QPalette()
        MainWindow.setAutoFillBackground(True)
        pe.setColor(QPalette.Window, Qt.lightGray)  # 设置背景色
        pe.setBrush(QPalette.Background, QBrush(QPixmap("./images/bg.jpg")))
        # pe.setColor(QPalette.Background,Qt.blue)
        MainWindow.setPalette(pe)

        self.label.setText(_translate("MainWindow", "当前时间："))
        self.label_3.setText(_translate("MainWindow", str(init_time)))
        self.stop_timer_btn.setText(_translate("MainWindow", "暂停时间"))
        self.start_timer_btn.setText(_translate("MainWindow", "继续时间"))
        self.timer_status.setText(_translate("MainWindow", "时间状态：正常"))
        self.pushButton.setText(_translate("MainWindow", "打开地图"))
        self.pushButton_2.setText(_translate("MainWindow", "关闭窗口"))
        self.label_2.setText(_translate("MainWindow", "选择任务："))
        self.label_5.setText(_translate("MainWindow", "出发地"))
        self.comboBox.setItemText(0, _translate("MainWindow", "北京"))
        self.comboBox.setItemText(1, _translate("MainWindow", "上海"))
        self.comboBox.setItemText(2, _translate("MainWindow", "广州"))
        self.comboBox.setItemText(3, _translate("MainWindow", "哈尔滨"))
        self.comboBox.setItemText(4, _translate("MainWindow", "沈阳"))
        self.comboBox.setItemText(5, _translate("MainWindow", "天津"))
        self.comboBox.setItemText(6, _translate("MainWindow", "兰州"))
        self.comboBox.setItemText(7, _translate("MainWindow", "成都"))
        self.comboBox.setItemText(8, _translate("MainWindow", "贵阳"))
        self.comboBox.setItemText(9, _translate("MainWindow", "武汉"))
        self.comboBox.setItemText(10, _translate("MainWindow", "海口"))
        self.comboBox.setItemText(11, _translate("MainWindow", "乌鲁木齐"))
        self.label_6.setText(_translate("MainWindow", "目的地："))
        self.comboBox_2.setItemText(0, _translate("MainWindow", "北京"))
        self.comboBox_2.setItemText(1, _translate("MainWindow", "上海"))
        self.comboBox_2.setItemText(2, _translate("MainWindow", "广州"))
        self.comboBox_2.setItemText(3, _translate("MainWindow", "哈尔滨"))
        self.comboBox_2.setItemText(4, _translate("MainWindow", "沈阳"))
        self.comboBox_2.setItemText(5, _translate("MainWindow", "天津"))
        self.comboBox_2.setItemText(6, _translate("MainWindow", "兰州"))
        self.comboBox_2.setItemText(7, _translate("MainWindow", "成都"))
        self.comboBox_2.setItemText(8, _translate("MainWindow", "贵阳"))
        self.comboBox_2.setItemText(9, _translate("MainWindow", "武汉"))
        self.comboBox_2.setItemText(10, _translate("MainWindow", "海口"))
        self.comboBox_2.setItemText(11, _translate("MainWindow", "乌鲁木齐"))
        self.label_7.setText(_translate("MainWindow", "任务模式："))
        self.checkBox_3.setText(_translate("MainWindow", "不限时间"))
        self.checkBox.setText(_translate("MainWindow", "限时"))
        self.label_8.setText(_translate("MainWindow", "限制时间："))
        self.pushButton_3.setText(_translate("MainWindow", "提交任务"))
        self.label_4.setText(_translate("MainWindow", "选择旅客："))
        self.comboBox_3.setItemText(0, _translate("MainWindow", "旅客0"))
        self.comboBox_3.setItemText(1, _translate("MainWindow", "旅客1"))
        self.comboBox_3.setItemText(2, _translate("MainWindow", "旅客2"))
        self.comboBox_3.setItemText(3, _translate("MainWindow", "旅客3"))
        self.comboBox_3.setItemText(4, _translate("MainWindow", "旅客4"))
        self.comboBox_3.setItemText(5, _translate("MainWindow", "旅客5"))

    # 更新时间及相关模块
    def time_update(self,timedelta):
        self.label_3.setText(str(init_time + datetime.timedelta(hours=timedelta)))
        self.update_traveller_state()
        self.change_dep_combo()
        self.log.flush()
        if self.map_on:
            self.map.update_traveller_text_signal.emit(self.traveller_list, self.time_thread.timedelta)

    # 修改任务提交按钮状态
    def change_dep_combo(self):
        self.comboBox.setEnabled(True)
        traveller_id = int(self.comboBox_3.currentText()[-1])
        # 如果没有收到过任务，或者收到任务但是任务不能执行，直接return
        if len(self.traveller_list[traveller_id]['route'])==0:
            self.pushButton_3.setText("提交任务")
            return
        if self.traveller_list[traveller_id]['arrived']==1:
            # 当前是闲置状态
            self.pushButton_3.setText("提交任务")
            # 旅客在某个城市等待，出发地指定为该城市
            if self.traveller_list[traveller_id]['in_trans'] == 0:
                traveller_present_loc = self.traveller_list[traveller_id]['present_city']
                # 如果还没收到过任务，可以从任何地方开始
                if traveller_present_loc == "":
                    return
                index = city_id[traveller_present_loc]['id']
                self.comboBox.setCurrentIndex(index)
                self.comboBox.setDisabled(True)

        else:
            # 当前是旅途中
            self.pushButton_3.setText("修改行程")
            # 旅客在某个城市等待，出发地指定为该城市
            if self.traveller_list[traveller_id]['in_trans'] == 0:
                traveller_present_loc = self.traveller_list[traveller_id]['present_city']
                index = city_id[traveller_present_loc]['id']
                self.comboBox.setCurrentIndex(index)
                self.comboBox.setDisabled(True)

    # 生成任务并计算方案
    def get_mission(self):
        #print("get_mission...")
        dep = self.comboBox.currentText()
        dest = self.comboBox_2.currentText()
        time_limit = self.limit_time_input.value()
        plan = int(self.checkBox.isChecked())
        traveller_id = int(self.comboBox_3.currentText()[-1])
        # 异常处理
        if (dep == dest):
            reply = QMessageBox.about(self, '错误', '出发地和目的地不能是同一城市')
            return
        if self.traveller_list[traveller_id]['in_trans'] == 1:
            reply = QMessageBox.about(self, '错误', '该旅客正在交通工具上，请等待该旅客抵达城市后再修改计划')
            return

        mission_dict = {'departure': dep, 'destination': dest, 'time_limit': time_limit, 'plan': plan,
                        'start_time':self.time_thread.timedelta,'traveller_id': traveller_id}
        #self.mission_queue.append(mission_dict)
        print(mission_dict)
        self.get_route(mission_dict)

    # 计算最佳路线
    def get_route(self,mission_dict):
        # print("get_routing...")
        get_best_route(mission_dict,self.traveller_list,self.city_graph)
        # 如果无法到达目的地，则弹出提示框
        if len(self.traveller_list[mission_dict['traveller_id']]['route'])==0:
            reply = QMessageBox.about(self, '错误', '旅客{}无法到达目的地，请修改时限！！'.format(mission_dict['traveller_id']))
            self.traveller_list[mission_dict['traveller_id']]['destination']==''
            self.traveller_list[mission_dict['traveller_id']]['departure'] == ''

        #print(self.traveller_list)
        self.print_route(self.traveller_list[mission_dict['traveller_id']])

    # 方案展示模块
    def print_route(self,traveller):
        if len(traveller['route']) == 0:
            print("旅客{}无法到达目的地，请修改时限！！".format(traveller['id']))
            return
        output_str = ""
        output_str += "=======================旅客{}的路线已规划完毕！=======================\n".format(traveller['id'])
        output_str += "==============================时间详情==============================\n"
        output_str += "旅途耗时：{}小时\n".format(traveller['time'])
        output_str += "预计出发时间：{}\n".format(init_time+datetime.timedelta(hours=traveller['start_time']))
        output_str += "预计抵达时间：{}\n".format(init_time + datetime.timedelta(hours=traveller['start_time'])
                                                                          +datetime.timedelta(hours=traveller['time']))
        output_str += "==============================风险详情==============================\n"
        output_str += "感染风险：{}\n".format(traveller['risk'])
        output_str += "==============================详细安排==============================\n"
        number = 0
        #print(traveller['route'])
        for trans in traveller['route']:
            dep = trans['departure']
            dest = trans['destination']
            id = trans['id']
            way = trans['way']
            if way == '飞机':
                trans_way = '✈'
            elif way == '火车':
                trans_way = '🚝'
            else:
                trans_way = '🚗'
            dep_time = init_time + datetime.timedelta(hours=(traveller['start_time'] + trans['time_interval']))
            output_str += "{}#{}: {}➡{}\t\t\t交通工具：{}\n".format(trans_way,number,dep,dest,way)
            output_str += "班次: {}\n".format(id)
            output_str += "出发时间：{}\n".format(str(init_time + datetime.timedelta(hours=traveller['start_time'] +trans['time_interval'])))
            output_str += "抵达时间：{}\n\n".format(str(init_time + datetime.timedelta(hours=traveller['start_time'] +trans['trans_time'] + trans['time_interval'])))
            #output_str += "{},旅客{}由{}乘坐{}号{}前往{}\n".format(dep_time, traveller['id'], dep, id, way, dest)
            number+=1
        self.textBrowser_2.setText(output_str)
        self.log.write(output_str)

    # 每小时更新旅客的状态
    def update_traveller_state(self):
        present_time = self.time_thread.timedelta
        print("当前时间为：{}".format(init_time + datetime.timedelta(hours=present_time)))
        self.log.write("当前时间为：{}\n\n".format(init_time + datetime.timedelta(hours=present_time)))
        for traveller in self.traveller_list:
            # print(travller)
            if len(traveller['route'])==0 :
                continue
            route_index = traveller['route_index']
            present_route = traveller['route'][route_index]

            if traveller['arrived'] == 1:
                print("旅客{}已到达目的地，等待下一条指令".format(traveller['id']))
                self.log.write("旅客{}已到达目的地，等待下一条指令\n\n".format(traveller['id']))
                traveller['present_city'] = traveller['destination']
                continue
            dep_time = present_route['depart_time']
            arr_time = present_route['arrive_time']

            # 判断乘客在等待还是正在车上
            # in_trans 0 表示在城市里等待，in_trans 1 表示在交通工具上
            if traveller['in_trans']==0 and present_time%24 == dep_time:
                print(
                    "旅客{}目前正在{}前往{}的{}次{}上".format(traveller['id'], present_route['departure'],
                                                   present_route['destination'],
                                                   present_route['id'], present_route['way']))
                self.log.write("旅客{}目前正在{}前往{}的{}次{}上\n\n".format(traveller['id'], present_route['departure'],
                                                                  present_route['destination'],
                                                                  present_route['id'], present_route['way']))
                traveller['in_trans'] = 1
            elif traveller['in_trans']==1 and ((dep_time > arr_time and (present_time % 24 > dep_time or present_time % 24 < arr_time)) or (dep_time < arr_time and (
                    present_time % 24 > dep_time and present_time % 24 < arr_time))):
                print(
                    "旅客{}目前正在{}前往{}的{}次{}上".format(traveller['id'], present_route['departure'],
                                                   present_route['destination'],
                                                   present_route['id'], present_route['way']))
                self.log.write("旅客{}目前正在{}前往{}的{}次{}上\n\n".format(traveller['id'], present_route['departure'],
                                                   present_route['destination'],
                                                   present_route['id'], present_route['way']))
                #traveller['in_trans']=1
            elif traveller['in_trans']==1 and present_time % 24 == present_route['arrive_time']:
                print("旅客{}抵达{}".format(traveller['id'], present_route['destination']))
                self.log.write("旅客{}抵达{}\n\n".format(traveller['id'], present_route['destination']))
                if (traveller['route_index'] == len(traveller['route']) - 1):
                    traveller['arrived'] = 1
                else:
                    traveller['route_index'] = route_index + 1
                traveller['in_trans'] = 0
                traveller['present_city'] = present_route['destination']
            else:
                print("旅客{}在{}等待{}次{}".format(traveller['id'], present_route['departure'],
                                              present_route['id'], present_route['way']))
                self.log.write("旅客{}在{}等待{}次{}\n\n".format(traveller['id'], present_route['departure'],
                                              present_route['id'], present_route['way']))
                traveller['in_trans'] = 0
                traveller['present_city'] = present_route['departure']

    def open_map(self):
        self.map_on = True
        self.map.update_traveller_text_signal.emit(self.traveller_list,self.time_thread.timedelta)

# 地图页面
class Ui_Dialog(QWidget):
    update_traveller_text_signal = pyqtSignal(list,int)
    draw_map_signal = pyqtSignal(dict)

    def __init__(self):
        super(Ui_Dialog,self).__init__()

    def initSlot(self):
        self.update_traveller_text_signal.connect(self.update_traveller)

    def setupUi(self, Dialog):
        Dialog.setObjectName("Map")
        Dialog.resize(1180, 630)
        Dialog.setWindowTitle("当前旅行状态查询页")
        self.textBrowser = QtWidgets.QTextBrowser(Dialog)
        self.textBrowser.setGeometry(QtCore.QRect(770, 10, 400, 600))
        self.textBrowser.setObjectName("textBrowser")
        self.textBrowser.setReadOnly(True)
        self.webEngineView = QtWebEngineWidgets.QWebEngineView(Dialog)
        self.webEngineView.setGeometry(QtCore.QRect(-60, 0, 821, 611))
        self.webEngineView.setUrl(QtCore.QUrl.fromLocalFile(
            "/当前旅行状态查询页.html"))
        self.webEngineView.setObjectName("webEngineView")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

        self.initSlot()

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "当前旅行状态查询页"))

    # 更新旅客信息
    def update_traveller(self,traveller_list,timedelta):
        present_time = timedelta
        travel_line_list = {"旅客0":{},"旅客1":{},"旅客2":{},"旅客3":{},"旅客4":{},"旅客5":{}}
        output_str = ""
        output_str += "当前时间为：{}\n\n".format(init_time + datetime.timedelta(hours=present_time))
        output_str += "-"*45+'\n\n'
        for traveller in traveller_list:
            traveller_name = "旅客"+str(traveller['id'])
            if len(traveller['route']) == 0:
                continue

            route_index = traveller['route_index']
            present_route = traveller['route'][route_index]
            travel_line_list[traveller_name]['departure'] = present_route['departure']
            travel_line_list[traveller_name]['way'] = present_route['way']
            travel_line_list[traveller_name]['destination'] = present_route['destination']
            if traveller['arrived'] == 1:
                output_str+="旅客{}已到达目的地{}，等待下一条指令\n\n".format(traveller['id'],traveller['destination'])
                travel_line_list[traveller_name]['on_route']= 2
                continue
            dep_time = present_route['depart_time']
            arr_time = present_route['arrive_time']

            # 判断乘客在等待还是正在车上
            # in_trans 0 表示在城市里等待，in_trans 1 表示在交通工具上
            if ((present_time % 24 >= dep_time or present_time % 24 < arr_time) and dep_time > arr_time) or (
                    present_time % 24 >= dep_time and present_time < arr_time):
                output_str+= "旅客{}目前正在{}前往{}的{}次{}上\n\n".format(traveller['id'], present_route['departure'],
                                                   present_route['destination'],
                                                   present_route['id'], present_route['way'])
                # 添加航班线
                travel_line_list[traveller_name]['on_route']= 1
            elif present_time % 24 == present_route['arrive_time']:
                output_str += "旅客{}抵达{}\n\n".format(traveller['id'], present_route['destination'])
                # 添加城市点
                travel_line_list[traveller_name]['on_route'] = 0
            else:
                output_str += "旅客{}在{}等待{}次{}\n\n".format(traveller['id'], present_route['departure'],
                                              present_route['id'], present_route['way'])
                # 添加城市点
                travel_line_list[traveller_name]['on_route'] = 0
            output_str += "-" * 45 + '\n\n'
            output_str += '旅客{}接下来的行程\n\n'.format(traveller['id'])
            for i in range(route_index,len(traveller['route'])):
                trans = traveller['route'][i]
                output_str += "{},乘坐{}离开{},前往{}\n\n".format(str(init_time+datetime.timedelta(hours=trans['time_interval']+traveller['start_time'])),trans['way'],
                                                            trans['departure'],trans['destination'])
                output_str += "{},抵达{}\n\n".format(str(init_time+datetime.timedelta(hours=trans['time_interval']+trans['trans_time']+traveller['start_time'])),
                                                   trans['destination'])
            output_str += "-" * 45 + '\n\n'

        generate_travel_state_page(travel_line_list)
        self.textBrowser.setText(output_str)
        self.webEngineView.setUrl(QtCore.QUrl.fromLocalFile(
            "/当前旅行状态查询页.html"))

# 时间线程
class TimeThread(QThread):
    time_update_signal = pyqtSignal(int)
    get_route_signal = pyqtSignal()

    def __init__(self):
        super(TimeThread, self).__init__()
        # 程序从开始到现在的时间间隔
        self.timedelta = 0
        self.timer = 0
        self.is_on = True

    def run(self):
        while True:
            if self.is_on:
                # time_gap秒改变1h
                if self.timer == time_gap:
                    self.timedelta = self.timedelta + 1
                    self.time_update_signal.emit(self.timedelta)
                    self.timer = 0
                else:
                    self.timer = self.timer + 1
            self.sleep(1)

    def stop_timer(self):
        self.is_on = False

    def start_timer(self):
        self.is_on = True

from PyQt5 import QtWebEngineWidgets

if __name__ == '__main__':
    app = QApplication(sys.argv)

    mw = QMainWindow()
    gui = Ui_MainWindow()
    gui.setupUi(mw)
    mw.show()
    sys.exit(app.exec_())
