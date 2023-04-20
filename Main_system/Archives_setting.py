import re
import toml

class Setting:
    """读取配置文件,检查数据"""
    instance = None
    # server
    _server_host = None
    _server_port = None
    # mysql
    _db_host = None
    _db_port = None
    _db_user = None
    _db_password = None
    _db_name = None
    # system
    _save_archives_data = None
    _save_alarm_data = None
    _view_data_permission = None
    _control_permission = None
    _system_setting_permission = None
    _add_user_permission = None

    def __new__(cls, *args, **kwargs):
        if cls.instance:
            return cls.instance
        else:
            cls.instance = object.__new__(cls)
            return cls.instance

    def __init__(self, **kwargs):
        self.server_host = kwargs.get('server_host')
        self.server_port = kwargs.get('server_port')
        self.db_host = kwargs.get('db_host')
        self.db_port = kwargs.get('db_port')
        self.db_user = kwargs.get('db_user')
        self.db_password = kwargs.get('db_password')
        self.db_name = kwargs.get('db_name')
        self.view_data_permission = kwargs.get('view_data_permission')
        self.control_permission = kwargs.get('control_permission')
        self.system_setting_permission = kwargs.get('system_setting_permission')
        self.add_user_permission = kwargs.get('add_user_permission')
        self.client_window = kwargs.get('client_window')

    @property
    def server_host(self):
        return self._server_host

    @server_host.setter
    def server_host(self,host):
        ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if isinstance(host, str) and re.match(ip_pattern, host):
            self._server_host = host
        else:
            self._server_host = ''


    @property
    def server_port(self):
        return self._server_port

    @server_port.setter
    def server_port(self, port):
        if isinstance(port, int) and 65536 >= port >= 0:
            self._server_port = port
        else:
            self._server_port = 0

    @property
    def db_host(self):
        return self._db_host

    @db_host.setter
    def db_host(self, host):
        ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if isinstance(host, str) and re.match(ip_pattern, host):
            self._db_host = host
        else:
            self._db_host = ''

    @property
    def db_port(self):
        return self._db_port

    @db_port.setter
    def db_port(self, port):
        if isinstance(port, int) and 65536 >= port >= 0:
            self._db_port = port
        else:
            self._db_port = 0

    @property
    def db_user(self):
        return self._db_user

    @db_user.setter
    def db_user(self, user):
        if user and isinstance(user,str):
            self._db_user = user
        else:
            self._db_user = ''

    @property
    def db_password(self):
        return self._db_password

    @db_password.setter
    def db_password(self, pwd):
        if pwd and isinstance(pwd,str):
            self._db_password = pwd
        else:
            self._db_password = ''

    @property
    def db_name(self):
        return self._db_name

    @db_name.setter
    def db_name(self, name):
        if name and isinstance(name,str):
            self._db_name = name
        else:
            self._db_name = ''

    @property
    def view_data_permission(self):
        return self._view_data_permission

    @view_data_permission.setter
    def view_data_permission(self, lv):
        if isinstance(lv, int) and lv in list(range(1, 4)):
            self._view_data_permission = lv
        else:
            self._view_data_permission = 0

    @property
    def control_permission(self):
        return self._control_permission

    @control_permission.setter
    def control_permission(self, lv):
        if isinstance(lv, int) and lv in list(range(1, 4)):
            self._control_permission = lv
        else:
            self._control_permission = 0

    @property
    def system_setting_permission(self):
        return self._system_setting_permission

    @system_setting_permission.setter
    def system_setting_permission(self, lv):
        if isinstance(lv, int) and lv in list(range(1, 4)):
            self._system_setting_permission = lv
        else:
            self._system_setting_permission = 0

    @property
    def add_user_permission(self):
        return self._add_user_permission

    @add_user_permission.setter
    def add_user_permission(self, lv):
        if isinstance(lv, int) and lv in list(range(1, 4)):
            self._add_user_permission = lv
        else:
            self._add_user_permission = 0


class GetSetSetting:
    """对配置类读写操作"""
    toml_data = {}
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance:
            return cls.instance
        else:
            cls.instance = object.__new__(cls)
            return cls.instance

    def __init__(self):
        """初始化类 读取toml配置文件数据"""
        try:
            with open('./setting.toml') as f:
                self.toml_data = toml.load(f)
        except:
            self.toml_data = {}

    @property
    def get(self):
        """获取数据"""
        obj = Setting(**self.toml_data)
        return obj

    def set(self, check=0, **kwargs):
        """传入并检查传入的数据"""
        argv = kwargs
        obj = Setting(**argv)
        dic = obj.__dict__
        for ker, value in dic.items():
            if value:
                continue
            else:
                return False
        if check == 0:
            self.write_setting(obj)
        return True

    def write_setting(self, obj):
        """数据写入toml文件"""
        data = self.toml_data
        data['server_host'] = obj.server_host
        data['server_port'] = obj.server_port
        data['db_host'] = obj.db_host
        data['db_port'] = obj.db_port
        data['db_user'] = obj.db_user
        data['db_password'] = obj.db_password
        data['db_name'] = obj.db_name
        data['view_data_permission'] = obj.view_data_permission
        data['control_permission'] = obj.control_permission
        data['system_setting_permission'] = obj.system_setting_permission
        data['add_user_permission'] = obj.add_user_permission
        with open('./setting.toml','w') as f:
            toml.dump(data, f)

    @staticmethod
    def check_setting_file():
        obj = GetSetSetting()
        if obj.toml_data == {}:
            return False
        data_is_correct = obj.set(check=1, **obj.toml_data)
        if data_is_correct is False:
            return False
        return True
