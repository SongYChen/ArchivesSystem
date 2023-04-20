import sys
import time
import threading
from PyQt5.QtGui import QCloseEvent,QIcon,QMovie
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox
from PyQt5.Qt import QTimer, QTime, QStandardItemModel, QHeaderView, QStandardItem
from PyQt5.QtCore import Qt, QProcess, QByteArray

from UI_code.home_ui import Ui_home
from UI_code.login_ui import Ui_login
from UI_code.manual_control import Ui_manual
from UI_code.history_hum import Ui_history_hum
from UI_code.history_gas import Ui_history_gas
from UI_code.history_temp import Ui_history_temp
from UI_code.login_dialog import Ui_login_dialog
from UI_code.history_dust import Ui_history_dust
from UI_code.history_alarm import Ui_history_alarm
from UI_code.setting_ui import Ui_setting_ui
from UI_code.welcome import Ui_MainWindow as welcome_window
from UI_code.db_edit import Ui_db_edit
from UI_code.client import Ui_client

from Archives_server import SystemServer
from Archives_db import QueryDBData, MutationDBData, DB
from Archives_setting import GetSetSetting


class LoginUI(QMainWindow, Ui_login):

    def __init__(self):
        super(LoginUI, self).__init__()
        self.setupUi(self)
        self.login_btn.clicked.connect(self.login_fun)

    def open(self):
        welcome.open()
        self.setFixedSize(970, 530)

    def login_fun(self):
        if self.account_box.text():
            acc = self.account_box.text()
        else:
            QMessageBox.warning(self, "Login", "请输入账号！")
            return

        if self.password_box.text():
            psw = self.password_box.text()
        else:
            QMessageBox.warning(self, "Login", "请输入密码！")
            return
        if DB.check_db_connect():
            res = QueryDBData.matching_user_info(acc, psw)
            if res and res[1] != 0:
                login_dia.label.setText(f"用户：{str(res[0])} 登陆成功!")
                home.user_name_lab.setText(str(res[0]))
                home.level_lab.setText(str(res[1]))
                if GetSetSetting.check_setting_file():
                    self.close()
                    login_dia.open()
                else:
                    QMessageBox.warning(self, "配置文件错误", "配置文件异常，请检查系统配置！")
                    if (cfg.get.system_setting_permission and res[1] >= cfg.get.system_setting_permission) or (
                            cfg.get.system_setting_permission == 0 and res[1] == 3):
                        self.hide()
                        setting.exit_flag = 1
                        setting.open()
                    else:
                        QMessageBox.warning(self, "配置文件错误", f"用户：{res[0]} 无设置权限！")
            elif res and res[1] == 0:
                login_dia.label.setText(f"{str(res[0])} 无登录权限！")
                login_dia.open()
            else:
                login_dia.label.setText("账号或密码错误！")
                login_dia.open()
        else:
            QMessageBox.warning(self, "数据库连接失败", "数据库连接失败,请检查数据库配置！")
            db_edit.open()


class LoginDialog(QMainWindow, Ui_login_dialog):
    def __init__(self):
        super(LoginDialog, self).__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.go_home_ui)

    def open(self):
        self.show()

    def go_home_ui(self):
        if "登陆成功!" in self.label.text():
            self.close()
            login.close()
            home.open()
        else:
            login.account_box.setText("")
            login.password_box.setText("")
            self.close()


class HomeUI(QMainWindow, Ui_home):
    def __init__(self):
        super(HomeUI, self).__init__()
        self.setupUi(self)
        self.run_count = 0
        self.info_dic = {}
        self.db_dic = {}
        self.conn_obj = None
        self.main_win_exit.clicked.connect(self.close)
        self.conn_dev_btn.clicked.connect(self.build_connect)
        self.dis_dev_btn.clicked.connect(self.close_connect)
        self.conn_test_btn.clicked.connect(lambda: self.connect_test(self.conn_obj))
        self.manual_btn.clicked.connect(self.show_manual)
        self.auto_switch_btn.clicked.connect(self.switch_auto)
        self.his_temp_btn.clicked.connect(self.show_his_temp)
        self.his_hum_btn.clicked.connect(self.show_his_hum)
        self.his_gas_btn.clicked.connect(self.show_his_gas)
        self.his_dust_btn.clicked.connect(self.show_his_dust)
        self.his_warring_btn.clicked.connect(self.show_his_alarm)
        self.admin_btn.clicked.connect(self.show_setting_ui)

    def open(self):
        self.setFixedSize(1081, 785)
        self.show()
        self.connect_lab.setText('未连接')
        self.server_ip_lab.setText(cfg.get.server_host)
        self.server_port_lab.setText(str(cfg.get.server_port))
        self.auto_switch_btn.setDisabled(1)
        self.manual_btn.setDisabled(1)
        if int(self.level_lab.text()) < cfg.get.system_setting_permission:
            self.admin_btn.setDisabled(1)
        if int(self.level_lab.text()) < cfg.get.view_data_permission:
            self.his_warring_btn.setDisabled(1)
            self.his_dust_btn.setDisabled(1)
            self.his_gas_btn.setDisabled(1)
            self.his_hum_btn.setDisabled(1)
            self.his_temp_btn.setDisabled(1)
        self.dis_local_time()

    def build_connect(self):
        conn_obj = SystemServer()
        if conn_obj.client and self.connect_lab.text() == '未连接':
            self.conn_obj = conn_obj
            self.connect_lab.setText('已连接')
            self.connect_lab.setStyleSheet('color:lime;')
            self.auto_status_lab.setText('开启')
            self.auto_switch_btn.setText('关闭')
            if int(self.level_lab.text()) >= cfg.get.control_permission:
                self.manual_btn.setEnabled(1)
                self.auto_switch_btn.setEnabled(1)
            self.info_dic = self.conn_obj.get_sensor_info()
            recv_thread = threading.Thread(target=self.recv_data,daemon=True)
            recv_thread.start()
            self.dis_archives_info()
            if client:
                client.open()
        else:
            QMessageBox.information(self, "Connection", "服务器连接失败！")

    def close_connect(self):
        conn_obj = SystemServer()
        if conn_obj.client and self.connect_lab.text() == '已连接':
            self.connect_lab.setText('未连接')
            self.connect_lab.setStyleSheet('color:red;')
            self.dis_temp.__timer.stop()
            self.dis_hum.display(0)
            self.dis_gas.display(0)
            self.dis_temp.display(0)
            self.dis_dust.display(0)
            self.auto_status_lab.setText('关闭')
            self.auto_switch_btn.setText('开启')
            self.auto_switch_btn.setDisabled(1)
            self.manual_btn.setEnabled(1)
            if client:
                client.close()
            conn_obj.close_server_connect()
        else:
            QMessageBox.information(self, "Connection", "服务器未连接！")

    def connect_test(self, conn):
        try:
            data = conn.get_sensor_info()
            if data.get('conn') == 1:
                QMessageBox.information(self, "Connection", "服务器已连接！")
            else:
                QMessageBox.information(self, "Connection", "服务器未连接！")
        except:
            QMessageBox.information(self, "Connection", "服务器未连接！")

    def dis_local_time(self):
        def update_time():
            self.time = QTime.currentTime()
            time_text = self.time.toString(Qt.DefaultLocaleLongDate)
            self.local_time_dis.setNumDigits(8)
            self.local_time_dis.display(time_text)

        update_time()
        self.local_time_dis.__timer = QTimer(self)
        self.local_time_dis.__timer.timeout.connect(update_time)
        self.local_time_dis.__timer.start(1000)

    def recv_data(self):
        while True:
            if self.conn_obj.client:
                self.info_dic = self.conn_obj.get_sensor_info()
            else:
                break

    def dis_archives_info(self):
        self.run_count = 0
        def update_info():
            if self.info_dic:
                temp = float(self.info_dic.get('temp')) if self.info_dic.get('conn') == 1 else 0
                high_temp = self.info_dic.get('high_temp') if self.info_dic.get('conn') == 1 else 0
                hum = int(self.info_dic.get('hum')) if self.info_dic.get('conn') == 1 else 0
                high_hum = self.info_dic.get('high_hum') if self.info_dic.get('conn') == 1 else 0
                dust = int(self.info_dic.get('dust')) if self.info_dic.get('conn') == 1 else 0
                gas = int(self.info_dic.get('gas')) if self.info_dic.get('conn') == 1 else 0
                high_gas = int(self.info_dic.get('high_gas')) if self.info_dic.get('conn') == 1 else 0
                high_dust = int(self.info_dic.get('high_dust')) if self.info_dic.get('conn') == 1 else 0
                fire = int(self.info_dic.get('fire')) if self.info_dic.get('conn') == 1 else 0
                ir = int(self.info_dic.get('ir_ray')) if self.info_dic.get('conn') == 1 else 0
                self.dis_temp.display(temp)
                self.dis_hum.display(hum)
                self.dis_dust.display(dust)
                self.dis_gas.display(gas)
                self.db_dic = {'temp':temp,'hum':hum,'dust':dust,'gas':gas}
                if self.run_count % 60 == 0:
                    self.save_data_to_db(self.db_dic)
                if self.run_count % 120 == 0:
                    send_id = threading.Thread(target=self.conn_obj.send_msg_to_server,args=('ID:15143939123',))
                    send_id.start()
                self.run_count += 1
                # 温度报警
                if high_temp == 1:
                    self.high_temp.setStyleSheet('background:red')
                    self.save_data_to_db(self.db_dic,('温度过高',temp))
                else:
                    self.high_temp.setStyleSheet('background:lime')
                # 湿度报警
                if high_hum == 1:
                    self.high_hum.setStyleSheet('background:red')
                    self.save_data_to_db(self.db_dic, ('湿度过高',hum))
                else:
                    self.high_hum.setStyleSheet('background:lime')
                # 灰尘报警
                if high_dust == 1:
                    self.high_dust.setStyleSheet('background:red')
                    self.save_data_to_db(self.db_dic, ('灰尘浓度过高',dust))
                else:
                    self.high_dust.setStyleSheet('background:lime')
                # 有害气体报警
                if high_gas == 1:
                    self.high_gas.setStyleSheet('background:red')
                    self.save_data_to_db(self.db_dic, ('有害气体浓度过高',gas))
                else:
                    self.high_gas.setStyleSheet('background:lime')
                # 火灾报警
                if fire == 1:
                    self.on_fire.setStyleSheet('background:red')
                    self.save_data_to_db(self.db_dic, ('火灾报警',1))
                else:
                    self.on_fire.setStyleSheet('background:lime')
                # 防盗报警
                if ir == 1:
                    self.on_theft.setStyleSheet('background:red')
                    self.save_data_to_db(self.db_dic, ('防盗报警',1))
                else:
                    self.on_theft.setStyleSheet('background:lime')
        update_info()
        self.dis_temp.__timer = QTimer(self)
        self.dis_temp.__timer.timeout.connect(update_info)
        self.dis_temp.__timer.start(500)

    def save_data_to_db(self, data, flag=('',0)):
        temp = data.get('temp')
        hum = data.get('hum')
        dust = data.get('dust')
        gas = data.get('gas')
        if flag[0] and flag[1]:
            MutationDBData.operate_archives_info(time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                                                 data=flag[1], type=flag[0])
        MutationDBData.operate_archives_info(temp=temp, hum=hum, dust=dust, gas=gas,
                                             time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    def switch_auto(self):
        conn_obj = SystemServer()
        if self.auto_switch_btn.text() == '开启':
            conn_obj.send_msg_to_server('Z')
            self.auto_status_lab.setText('开启')
            self.auto_switch_btn.setText('关闭')
        else:
            conn_obj.send_msg_to_server('S')
            self.auto_status_lab.setText('关闭')
            self.auto_switch_btn.setText('开启')

    def show_manual(self):
        manual.open()

    def show_his_temp(self):
        his_temp.open()

    def show_his_hum(self):
        his_hum.open()

    def show_his_gas(self):
        his_gas.open()

    def show_his_dust(self):
        his_dust.open()

    def show_his_alarm(self):
        his_alarm.open()

    def show_setting_ui(self):
        setting.open()

    def closeEvent(self, event: QCloseEvent):
        reply = QMessageBox.question(self, "Exit", "退出系统？", QMessageBox.Yes | QMessageBox.No)
        if reply == 16384:
            conn_obj = SystemServer()
            if conn_obj.client:
                conn_obj.close_server_connect()
            event.accept()
            sys.exit(0)
        else:
            event.ignore()


class ManualUi(QMainWindow, Ui_manual):
    def __init__(self):
        super(ManualUi, self).__init__()
        self.setupUi(self)
        self.manual_btn.clicked.connect(self.switch_manual_mode)
        self.light_btn.clicked.connect(self.switch_light_status)
        self.clear_btn.clicked.connect(self.switch_uv_status)
        self.wind_btn.clicked.connect(self.switch_wind_status)
        self.exit_btn.clicked.connect(self.close_frame)

    def open(self):
        self.manual_btn.setText('开启')
        home.auto_status_lab.setText('关闭')
        home.auto_switch_btn.setText('开启')
        self.wind_btn.setDisabled(1)
        self.light_btn.setDisabled(1)
        self.clear_btn.setDisabled(1)
        self.light_status.setText('关')
        self.clear_status.setText('关')
        self.wind_status.setText('关')
        self.show()

    def close_frame(self):
        if self.manual_btn.text() == '关闭':
            self.send_msg('Z')
        home.auto_status_lab.setText('开启')
        home.auto_switch_btn.setText('关闭')
        self.close()

    def send_msg(self, msg):
        conn_obj = SystemServer()
        send_thread = threading.Thread(target=conn_obj.send_msg_to_server, kwargs={'msg': msg}, daemon=True)
        send_thread.start()

    def switch_manual_mode(self):
        if self.manual_btn.text() == '开启':
            self.send_msg('S')
            self.manual_btn.setText('关闭')
            self.wind_btn.setEnabled(1)
            self.light_btn.setEnabled(1)
            self.clear_btn.setEnabled(1)
        else:
            self.send_msg('Z')
            self.manual_btn.setText('开启')
            self.wind_btn.setDisabled(1)
            self.light_btn.setDisabled(1)
            self.clear_btn.setDisabled(1)

    def switch_light_status(self):
        if self.light_btn.text() == '开启':
            self.send_msg('LDK')
            self.light_btn.setText('关闭')
            self.light_status.setText('开')
        else:
            self.send_msg('LDG')
            self.light_btn.setText('开启')
            self.light_status.setText('关')

    def switch_uv_status(self):
        if self.clear_btn.text() == '开启':
            self.send_msg('LZK')
            self.clear_btn.setText('关闭')
            self.clear_status.setText('开')
        else:
            self.send_msg('LZG')
            self.clear_btn.setText('开启')
            self.clear_status.setText('关')

    def switch_wind_status(self):
        if self.wind_btn.text() == '开启':
            self.send_msg('FSK')
            self.wind_btn.setText('关闭')
            self.wind_status.setText('开')
        else:
            self.send_msg('FSG')
            self.wind_btn.setText('开启')
            self.wind_status.setText('关')


class HistoryTemp(QMainWindow, Ui_history_temp):
    def __init__(self):
        super(HistoryTemp, self).__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.close)

    def open(self):
        data_list = QueryDBData.get_archives_data()
        if data_list:
            self.tableView.model = QStandardItemModel(len(data_list), 2)
            self.tableView.model.setHorizontalHeaderLabels(['时间', '温度'])
            # 水平方向标签拓展剩下的窗口部分，填满表格
            self.tableView.horizontalHeader().setStretchLastSection(True)
            # 水平方向，表格大小拓展到适当的尺寸
            self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            r = 0
            for data in data_list:
                item = QStandardItem(data.get('time'))
                self.tableView.model.setItem(r, 0, item)
                item = QStandardItem(str(data.get('temp')))
                self.tableView.model.setItem(r, 1, item)
                r += 1
        self.tableView.setModel(self.tableView.model)
        self.tableView.show()
        self.show()


class HistoryHum(QMainWindow, Ui_history_hum):
    def __init__(self):
        super(HistoryHum, self).__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.close)

    def open(self):
        data_list = QueryDBData.get_archives_data()
        if data_list:
            self.tableView.model = QStandardItemModel(len(data_list), 2)
            self.tableView.model.setHorizontalHeaderLabels(['时间', '湿度'])
            # 水平方向标签拓展剩下的窗口部分，填满表格
            self.tableView.horizontalHeader().setStretchLastSection(True)
            # 水平方向，表格大小拓展到适当的尺寸
            self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            r = 0
            for data in data_list:
                item = QStandardItem(data.get('time'))
                self.tableView.model.setItem(r, 0, item)
                item = QStandardItem(str(data.get('hum')))
                self.tableView.model.setItem(r, 1, item)
                r += 1
        self.tableView.setModel(self.tableView.model)
        self.tableView.show()
        self.show()


class HistoryGas(QMainWindow, Ui_history_gas):
    def __init__(self):
        super(HistoryGas, self).__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.close)

    def open(self):
        data_list = QueryDBData.get_archives_data()
        if data_list:
            self.tableView.model = QStandardItemModel(len(data_list), 2)
            self.tableView.model.setHorizontalHeaderLabels(['时间', '有害气体浓度'])
            # 水平方向标签拓展剩下的窗口部分，填满表格
            self.tableView.horizontalHeader().setStretchLastSection(True)
            # 水平方向，表格大小拓展到适当的尺寸
            self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            r = 0
            for data in data_list:
                item = QStandardItem(data.get('time'))
                self.tableView.model.setItem(r, 0, item)
                item = QStandardItem(str(data.get('gas')))
                self.tableView.model.setItem(r, 1, item)
                r += 1
        self.tableView.setModel(self.tableView.model)
        self.tableView.show()
        self.show()


class HistoryDust(QMainWindow, Ui_history_dust):
    def __init__(self):
        super(HistoryDust, self).__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.close)

    def open(self):
        data_list = QueryDBData.get_archives_data()
        if data_list:
            self.tableView.model = QStandardItemModel(len(data_list), 2)
            self.tableView.model.setHorizontalHeaderLabels(['时间', '灰尘浓度'])
            # 水平方向标签拓展剩下的窗口部分，填满表格
            self.tableView.horizontalHeader().setStretchLastSection(True)
            # 水平方向，表格大小拓展到适当的尺寸
            self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            r = 0
            for data in data_list:
                item = QStandardItem(data.get('time'))
                self.tableView.model.setItem(r, 0, item)
                item = QStandardItem(str(data.get('dust')))
                self.tableView.model.setItem(r, 1, item)
                r += 1
        self.tableView.setModel(self.tableView.model)
        self.tableView.show()
        self.show()


class HistoryAlarm(QMainWindow, Ui_history_alarm):
    def __init__(self):
        super(HistoryAlarm, self).__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.close)

    def open(self):
        data_list = QueryDBData.get_alarm_history_data()
        if data_list:
            self.tableView.model = QStandardItemModel(len(data_list), 3)
            self.tableView.model.setHorizontalHeaderLabels(['时间', '数据', '报警类型'])
            # 水平方向标签拓展剩下的窗口部分，填满表格
            self.tableView.horizontalHeader().setStretchLastSection(True)
            # 水平方向，表格大小拓展到适当的尺寸
            self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            r = 0
            for data in data_list:
                item = QStandardItem(data.get('time'))
                self.tableView.model.setItem(r, 0, item)
                item = QStandardItem(str(data.get('data')))
                self.tableView.model.setItem(r, 1, item)
                item = QStandardItem(str(data.get('type')))
                self.tableView.model.setItem(r, 2, item)
                r += 1
        self.tableView.setModel(self.tableView.model)
        self.tableView.show()
        self.show()


class SettingUI(QMainWindow, Ui_setting_ui):
    def __init__(self):
        super(SettingUI, self).__init__()
        self.exit_flag = 0
        self.setupUi(self)
        self.save_btn.clicked.connect(self.save_setting)
        self.exit_btn.clicked.connect(self.close)
        self.add_user_btn.clicked.connect(self.add_user)
        self.change_userp_btn.clicked.connect(self.update_perm)
        self.del_user_btn.clicked.connect(self.delete_user)

    def open(self):
        data = GetSetSetting()
        self.server_ip_text.setText(data.get.server_host)
        self.server_port_text.setText(str(data.get.server_port))
        self.db_ip_text.setText(data.get.db_host)
        self.db_port_text.setText(str(data.get.db_port))
        self.db_user_text.setText(data.get.db_user)
        self.db_psw_text.setText(data.get.db_password)
        self.db_name_text.setText(data.get.db_name)
        self.data_spinBox.setValue(data.get.view_data_permission)
        self.control_spinBox.setValue(data.get.control_permission)
        self.setting_spinBox.setValue(data.get.system_setting_permission)
        self.user_spinBox.setValue(data.get.add_user_permission)
        if int(home.level_lab.text()) < cfg.get.add_user_permission:
            self.setFixedSize(880, 500)
        if int(home.level_lab.text()) < self.setting_spinBox.value():
            self.setting_spinBox.setDisabled(1)
        if int(home.level_lab.text()) < self.data_spinBox.value():
            self.data_spinBox.setDisabled(1)
        if int(home.level_lab.text()) < self.user_spinBox.value():
            self.user_spinBox.setDisabled(1)
        if int(home.level_lab.text()) < self.control_spinBox.value():
            self.control_spinBox.setDisabled(1)
        self.show()

    def save_setting(self):
        data = {'server_host': self.server_ip_text.text(), 'server_port': int(self.server_port_text.text()),
                'db_host': self.db_ip_text.text(), 'db_port': int(self.db_port_text.text()),
                'db_user': self.db_user_text.text(), 'db_password': self.db_psw_text.text(),
                'db_name': self.db_name_text.text(), 'view_data_permission': self.data_spinBox.value(),
                'control_permission': self.control_spinBox.value(),
                'system_setting_permission': self.setting_spinBox.value(),
                'add_user_permission': self.user_spinBox.value(), "client_window": "hide"
                }
        is_success = cfg.set(**data)
        if is_success:
            reply = QMessageBox.question(self, "设置", "设置成功，是否重启应用？", QMessageBox.Yes | QMessageBox.No)
            if reply == 16384:
                conn = SystemServer()
                if conn:
                    conn.close_server_connect()
                    QTimer.singleShot(500, self.restart_app)

        else:
            QMessageBox.warning(self, "设置", "设置保存失败，请检查设置项！")

    def restart_app(self):
        # 启动新的进程
        app_path = QApplication.applicationFilePath()
        args = QApplication.instance().arguments()
        QProcess.startDetached(app_path, args)
        # 退出当前进程
        QApplication.quit()

    def add_user(self):
        if self.user_text.text():
            name = self.user_text.text()
        else:
            QMessageBox.warning(self, '添加用户', '请输入用户名！')
            return
        if self.acc_text.text():
            acc = self.acc_text.text()
        else:
            QMessageBox.warning(self, '添加用户', '请输入账号！')
            return
        if self.psw_text.text():
            pwd = self.psw_text.text()
        else:
            QMessageBox(self, '添加用户', '请输入密码！')
            return
        perm = self.add_userp_spinBox.value()
        info_dic = {'name': name, 'account': acc, 'password': pwd, 'permissions': perm}
        # 添加用户信息到数据库
        res = MutationDBData.operate_archives_info(**info_dic)
        if res[0]:
            QMessageBox.information(self, '添加用户', '添加成功！')
        else:
            QMessageBox.warning(self, '添加用户', res[1] + '添加失败！')

    def update_perm(self):
        if self.change_userp_text.text():
            acc = self.change_userp_text.text()
        else:
            QMessageBox.warning(self, '修改权限', '请输入账号！')
            return
        perm = self.change_userp_spinBox.value()
        info_dic = {'account': acc, 'update_permissions': perm}
        # 修改用户权限
        res = MutationDBData.operate_archives_info(**info_dic)
        if res[0]:
            QMessageBox.information(self, '修改权限', '修改成功！')
        else:
            QMessageBox.warning(self, '修改权限', res[1] + '修改失败！')

    def delete_user(self):
        if self.del_user_text.text():
            acc = self.del_user_text.text()
        else:
            QMessageBox.warning(self, '删除用户', '请输入账号！')
            return
        info_dic = {'delete_account': acc}
        # 删除用户
        res = MutationDBData.operate_archives_info(**info_dic)
        if res[0]:
            QMessageBox.information(self, '删除用户', '删除成功！')
        else:
            QMessageBox.information(self, '删除用户', res[1] + '删除失败！')

    def closeEvent(self, event: QCloseEvent):
        event.accept()
        if self.exit_flag == 1:
            sys.exit(0)


class WelcomeWindow(QMainWindow, welcome_window):
    def __init__(self):
        super(WelcomeWindow, self).__init__()
        self.setupUi(self)
        self.setWindowFlags(Qt.FramelessWindowHint)


    def open(self):
        movie = QMovie(':/new/welcome_3.gif', QByteArray(), self)
        movie.setCacheMode(QMovie.CacheAll)
        movie.setSpeed(15)
        self.label_4.setMovie(movie)
        movie.start()
        welcome.show()
        QTimer().singleShot(3500, self.close_win)

    def close_win(self):
        self.close()
        login.show()


class DBEdit(QMainWindow, Ui_db_edit):
    def __init__(self):
        super(DBEdit, self).__init__()
        self.setupUi(self)
        self.exit_btn.clicked.connect(self.close)
        self.ok_btn.clicked.connect(self.save_info)

    def open(self):
        self.show()
        self.ip_text.setText(cfg.get.db_host)
        self.port_text.setText(str(cfg.get.db_port))
        self.user_text.setText(cfg.get.db_user)
        self.pwd_text.setText(cfg.get.db_password)
        self.name_text.setText(cfg.get.db_name)

    def save_info(self):
        data = cfg.toml_data
        data['db_host'] = self.ip_text.text()
        data['db_port'] = int(self.port_text.text())
        data['db_user'] = self.user_text.text()
        data['db_password'] = self.pwd_text.text()
        data['db_name'] = self.name_text.text()
        is_success = cfg.set(**data)
        if is_success:
            reply = QMessageBox.question(self, "设置", "设置成功，是否重启应用？", QMessageBox.Yes | QMessageBox.No)
            if reply == 16384:
                QTimer.singleShot(500, self.restart_app)
        else:
            QMessageBox.warning(self, "设置", "数据库配置保存失败，请检查设置项！")

    def restart_app(self):
        # 启动新的进程
        app_path = QApplication.applicationFilePath()
        args = QApplication.instance().arguments()
        QProcess.startDetached(app_path, args)
        # 退出当前进程
        QApplication.quit()

    def closeEvent(self, event: QCloseEvent):
        event.accept()
        sys.exit(0)


class ClientWindow(QMainWindow, Ui_client):
    def __init__(self):
        super(ClientWindow, self).__init__()
        self.setupUi(self)
        self.data = ''
        self.exit_btn.clicked.connect(self.close)
        self.send_btn.clicked.connect(self.send_data)

    def open(self):
        conn_obj = SystemServer()
        self.show()
        self.ip_text.setText(cfg.get.server_host)
        self.port_text.setText(str(cfg.get.server_port))
        self.data_text.setText('start\r\n')
        sub_recv = threading.Thread(target=self.get_data, args=(conn_obj,), daemon=True)
        sub_recv.start()
        self.recv_data()

    def get_data(self, conn_obj):
        while True:
            self.data = conn_obj.get_sensor_info(flag=1)

    def recv_data(self):
        def recv():
            if self.data:
                self.data_text.setText(self.data+'\r\n'+ self.data_text.toPlainText())

        recv()
        self.data_text.__timer = QTimer(self)
        self.data_text.__timer.timeout.connect(recv)
        self.data_text.__timer.start(1000)

    def send_data(self):
        conn_obj = SystemServer()
        data = self.send_text.text()
        if data:
            send_thread = threading.Thread(target=conn_obj.send_msg_to_server,args=(data,),daemon=True)
            send_thread.start()
        self.send_text.clear()


if __name__ == "__main__":

    #  pyinstaller -D -w --icon=App.ico --name=ArchivesSYS --add-data "setting.toml;." Archives_ui.py

    # 创建QT应用对象
    app = QApplication(sys.argv)

    # 实例化配置文件对象
    cfg = GetSetSetting()

    # 实例化各个界面
    if cfg.get.client_window == 'show':
        client = ClientWindow()
        client.setWindowIcon(QIcon(':/new/colors.png'))
    else:
        client = None
    login = LoginUI()
    login.setWindowIcon(QIcon(':/new/colors.png'))
    login_dia = LoginDialog()
    login_dia.setWindowIcon(QIcon(':/new/colors.png'))
    home = HomeUI()
    home.setWindowIcon(QIcon(':/new/colors.png'))
    manual = ManualUi()
    manual.setWindowIcon(QIcon(':/new/colors.png'))
    his_temp = HistoryTemp()
    his_temp.setWindowIcon(QIcon(':/new/colors.png'))
    his_hum = HistoryHum()
    his_hum.setWindowIcon(QIcon(':/new/colors.png'))
    his_gas = HistoryGas()
    his_gas.setWindowIcon(QIcon(':/new/colors.png'))
    his_dust = HistoryDust()
    his_dust.setWindowIcon(QIcon(':/new/colors.png'))
    his_alarm = HistoryAlarm()
    his_alarm.setWindowIcon(QIcon(':/new/colors.png'))
    setting = SettingUI()
    setting.setWindowIcon(QIcon(':/new/colors.png'))
    welcome = WelcomeWindow()
    welcome.setWindowIcon(QIcon(':/new/colors.png'))
    db_edit = DBEdit()
    db_edit.setWindowIcon(QIcon(':/new/colors.png'))

    # 主入口为login画面,验证配置文件及数据库连接
    login.open()

    # 阻塞 等待应用结束
    sys.exit(app.exec_())
