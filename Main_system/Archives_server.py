import socket
import time

from Archives_setting import GetSetSetting

class SystemServer:
    """服务器通信类"""
    instance = None

    def __new__(cls, *args, **kwargs):
        """重写类的__new__函数，变为单例模式"""
        if cls.instance:
            return cls.instance
        else:
            cls.instance = object.__new__(cls)
            return cls.instance

    def __init__(self):
        """初始化对象 建立Socket连接"""
        self.cfg = GetSetSetting()
        self.host_ip = self.cfg.get.server_host
        self.port = self.cfg.get.server_port
        self.client = self.connect_to_server()

    def connect_to_server(self):
        """建立Socket连接"""
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.settimeout(3)
            client.connect((self.host_ip, self.port))
            for i in range(10):
                recv_data = client.recv(1024).decode("utf8")
                if recv_data[0] == 'H' and recv_data[1] == 'J':
                    return client
            return None
        except Exception:
            return None

    def get_sensor_info(self,flag=0):
        """接收服务器收到的下位机数据并处理"""
        if self.client:
            try:
                info_dic = {}
                #  HJ  21.4-0   47-0   011   \x  000    0      0     0       0
                # 连接  温度-高  湿度-高 pm2.5  占  有害  有害高   红外   烟雾   pm2.5高
                recv_data = self.client.recv(1024).decode("utf8")  # HJ 21.4-0 46-0 008 \x 000 y h w p
                if flag == 1:
                    return recv_data
                if 0 < len(recv_data) <= 21:
                    if recv_data[0] == 'H' and recv_data[1] == 'J':
                        info_dic['conn'] = 1
                        info_dic['temp'] = recv_data[2:6]
                        info_dic['high_temp'] = 1 if recv_data[6] == '1' else 0
                        info_dic['hum'] = recv_data[7:9]
                        info_dic['high_hum'] = 1 if recv_data[9] == '1' else 0
                        info_dic['dust'] = recv_data[10:13]
                        info_dic['high_dust'] = 1 if recv_data[20] == '1' else 0
                        info_dic['gas'] = recv_data[14:17]
                        info_dic['high_gas'] = 1 if recv_data[17] =='1' else 0
                        info_dic['ir_ray'] = 1 if recv_data[18]=='1' else 0
                        info_dic['fire'] = 1 if recv_data[19]=='1' else 0
                    elif recv_data[0] == 'C' and recv_data[1] == '0' and recv_data[2] == 'N':
                        info_dic['conn'] = 0
                        info_dic['temp'] = '0'
                        info_dic['high_temp']=0
                        info_dic['hum'] = '0'
                        info_dic['high_hum'] = 0
                        info_dic['dust'] = '0'
                        info_dic['gas'] = '0'
                        info_dic['ir_ray'] = 0
                        info_dic['fire'] = 0
                        info_dic['high_dust'] = 0
                        info_dic['high_gas'] = 0
                    return info_dic
                else:
                    return {}
            except Exception:
                return {}
        else:
            return {}

    def send_msg_to_server(self,msg:str):
        """发送命令到服务器"""
        if self.client and msg:
            self.client.send((msg+"\\" + "n").encode("GBK"))

    def close_server_connect(self):
        """关闭Socket连接"""
        if self.client:
            self.client.close()
