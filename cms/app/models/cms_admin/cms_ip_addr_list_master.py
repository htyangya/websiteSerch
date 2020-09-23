from datetime import datetime

from sqlalchemy.sql import text

from app import db


class CmsIpAddrListMaster(db.Model):
    __tablename__ = 'CMS_IP_ADDR_LIST_MASTER'
    ip_addr_list_id = db.Column(db.Integer, primary_key=True)
    ip_addr_list_name = db.Column(db.String(100))

    def __init__(self, ip_addr_list_id=None):
        self.ip_addr_list_id = ip_addr_list_id

    def get_ip_addr_list_name(self):
        return self.ip_addr_list_name

    def getCmsIpAddrListMaster(self, ip_addr_list_id):
        return db.session.query(CmsIpAddrListMaster).filter(CmsIpAddrListMaster.ip_addr_list_id == ip_addr_list_id).first()

    def getCmsIpAddrListMasters(self):
        selectSql = '''
            SELECT IP_ADDR_LIST_ID, IP_ADDR_LIST_NAME
              FROM CMS_IP_ADDR_LIST_MASTER m
             ORDER BY m.IP_ADDR_LIST_NAME
        '''
        t = text(selectSql)
        rst = db.session.execute(t, {})

        dic, array = {}, []
        for rowproxy in rst:
            for column, val in rowproxy.items():
                dic = {**dic, **{column: ('' if val is None else val)}}
            array.append(dic)
        return array
