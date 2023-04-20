import datetime
import pymysql
import threading
from translate import Translator
from Archives_setting import GetSetSetting


class DB:
    """父类 连接相关操作类"""
    cfg = GetSetSetting()
    _host = cfg.get.db_host
    _port = cfg.get.db_port
    _user = cfg.get.db_user
    _psw = cfg.get.db_password
    _db_name = cfg.get.db_name

    @classmethod
    def _create_db_connect(cls) -> (object, object) or None:
        """类方法：建立数据库连接"""
        try:
            con = pymysql.connect(host=cls._host, port=cls._port, user=cls._user, password=cls._psw,
                                  database=cls._db_name,
                                  charset='utf8')
            cur = con.cursor()
        except Exception:
            return None, None
        return con, cur

    @classmethod
    def _close_db_connect(cls, cur, con):
        """类方法：关闭数据库连接"""
        cur.close()
        con.close()

    @classmethod
    def check_db_connect(cls):
        conn = cls._create_db_connect()
        if conn[0] and conn[1]:
            return True
        else:
            return False


class QueryDBData(DB):
    """子类 查询相关操作类"""

    @classmethod
    def get_archives_data(cls, sort_field='datetime', sort_order='desc') -> list or None:
        """类方法：获取档案室环境数据"""
        con, cur = cls._create_db_connect()
        if con and cur:
            try:
                sql = f'select temperature,humidity,dust,gas,datetime from data order by {sort_field} {sort_order}'
                cur.execute(sql)
                data = cur.fetchall()
            except Exception:
                return None
            finally:
                cls._close_db_connect(cur, con)

            all_data_list = []
            if data:
                for data_tup in data:
                    data_dict = {"temp": float(data_tup[0]),
                                 "hum": float(data_tup[1]),
                                 "dust": float(data_tup[2]),
                                 "gas": float(data_tup[3]),
                                 "time": datetime.datetime.strptime(str(data_tup[4]), "%Y-%m-%d %H:%M:%S").strftime(
                                     "%Y-%m-%d %H:%M:%S")
                                 }
                    all_data_list.append(data_dict)
            else:
                return None
            return all_data_list

        else:
            return None

    @classmethod
    def get_alarm_history_data(cls, sort_field='datetime', sort_order='desc') -> list or None:
        """类方法：获取报警数据"""
        con, cur = cls._create_db_connect()
        if con and cur:
            try:
                sql = f'select datetime,data,type from alarm order by {sort_field} {sort_order}'
                cur.execute(sql)
                data = cur.fetchall()
            except Exception:
                return None
            finally:
                cls._close_db_connect(cur, con)

            all_data_list = []
            if data:
                for data_tup in data:
                    data_dict = {
                        "time": datetime.datetime.strptime(str(data_tup[0]), "%Y-%m-%d %H:%M:%S").strftime(
                            "%Y-%m-%d %H:%M:%S"),
                        "data": float(data_tup[1]),
                        'type': str(data_tup[2])
                    }
                    all_data_list.append(data_dict)
            else:
                return None
            return all_data_list

        else:
            return None

    @classmethod
    def matching_user_info(cls, acc: str, psw: str) -> (str, int) or None:
        """类方法：匹配账户信息，获取用户名和权限"""
        con, cur = cls._create_db_connect()
        if con and cur:
            try:
                sql = f"select name,permissions from user where account='{acc}' and password='{psw}'"
                cur.execute(sql)
                data = cur.fetchone()
            except Exception:
                return None
            finally:
                cls._close_db_connect(cur, con)
            if data:
                return data
            else:
                return None
        else:
            return None


class MutationDBData(DB):
    """子类 增删改数据相关操作类"""
    _add_user_res = [0,'']
    _del_user_res = [0,'']
    _change_perm_res = [0,'']

    @classmethod
    def _sub_thread_save_data(cls, temp, hum, dust, gas, time):
        """插入环境数据数据到表data"""
        con, cur = cls._create_db_connect()
        if con and cur:
            try:
                sql = f"INSERT INTO data (temperature, humidity, dust, gas, datetime) VALUES ({temp},{hum},{dust},{gas},'{time}');"
                r = cur.execute(sql)
                if r == 1:
                    con.commit()
            except Exception as e:
                print(e)
            finally:
                cls._close_db_connect(cur, con)

    @classmethod
    def _sub_thread_save_user(cls, name, acc, pwd, perm):
        """插入用户数据到表user"""
        r=0
        con, cur = cls._create_db_connect()
        if con and cur:
            try:
                sql = f"INSERT INTO user (name, account, password, permissions) VALUES ('{name}','{acc}','{pwd}',{perm});"
                cur.execute(sql)
                r= cur.rowcount
                if r == 1:
                    con.commit()
            except Exception as e:
                print(e)
            finally:
                cls._close_db_connect(cur, con)
                cls._add_user_res[0] = r

    @classmethod
    def _sub_thread_update_permissions(cls, account, perm):
        """更新用户权限到表user"""
        r=0
        con, cur = cls._create_db_connect()
        if con and cur:
            try:
                sql = f"update user set permissions = {perm} where account = '{account}';"
                cur.execute(sql)
                r = cur.rowcount
                if r == 1:
                    con.commit()
            except Exception as e:
                print(e)
            finally:
                cls._close_db_connect(cur, con)
                cls._change_perm_res[0] = r

    @classmethod
    def _sub_thread_delete_user(cls, account):
        """从表user中删除用户"""
        r=0
        con, cur = cls._create_db_connect()
        if con and cur:
            try:
                sql = f"DELETE FROM user WHERE account = '{account}';"
                cur.execute(sql)
                r = cur.rowcount
                if r == 1:
                    con.commit()
            except Exception as e:
                print(e)
            finally:
                cls._close_db_connect(cur, con)
                cls._del_user_res[0] = r

    @classmethod
    def _sub_thread_save_alarm(cls, time, data, type):
        """插入报警数据到表alarm"""
        con, cur = cls._create_db_connect()
        if con and cur:
            try:
                sql = f"INSERT INTO alarm (datetime,data,type) VALUES ('{time}',{data},'{type}');"
                r = cur.execute(sql)
                if r == 1:
                    con.commit()
            except Exception as e:
                print(e)
            finally:
                cls._close_db_connect(cur, con)

    @classmethod
    def operate_archives_info(cls, **kwargs):
        """创建子线程，进行修改添加数据操作"""
        info_dic = kwargs
        alarm_data = info_dic.get('data')
        temp = info_dic.get('temp')
        hum = info_dic.get('hum')
        dust = info_dic.get('dust')
        gas = info_dic.get('gas')
        time = info_dic.get('time')
        name = info_dic.get('name')
        alarm_type = info_dic.get('type')
        account = info_dic.get('account')
        password = info_dic.get('password')
        permissions = info_dic.get('permissions')
        update_permissions = info_dic.get('update_permissions')
        del_account = info_dic.get('delete_account')

        if temp:
            sub_save = threading.Thread(target=cls._sub_thread_save_data,
                                        kwargs={'temp': temp, 'hum': hum, 'dust': dust, 'gas': gas, 'time': time},
                                        daemon=True)
            sub_save.start()
        elif name:
            sub_save_user = threading.Thread(target=cls._sub_thread_save_user,
                                        kwargs={'name': name, 'acc': account, 'pwd': password, 'perm': permissions},
                                        daemon=True)
            sub_save_user.start()
            return cls._add_user_res
        elif alarm_type and alarm_data:
            sub_alarm = threading.Thread(target=cls._sub_thread_save_alarm,
                                         kwargs={'time': time, 'data': alarm_data, 'type': alarm_type},
                                         daemon=True)
            sub_alarm.start()
        elif update_permissions and account:
            sub_update_perm = threading.Thread(target=cls._sub_thread_update_permissions,
                                               kwargs={'account': account, 'perm': update_permissions},
                                               daemon=True)
            sub_update_perm.start()
            return cls._change_perm_res
        elif del_account:
            sub_del_user = threading.Thread(target=cls._sub_thread_delete_user,
                                            kwargs={'account': del_account},
                                            daemon=True)
            sub_del_user.start()
            return cls._del_user_res
        else:
            return
