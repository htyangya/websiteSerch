from datetime import datetime

from markupsafe import Markup
from sqlalchemy.sql import text

from app import db


class CmsIpAddrList(db.Model):
    __tablename__ = 'CMS_IP_ADDR_LIST'
    ip_addr_list_id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(20), primary_key=True)
    subnet_mask = db.Column(db.String(20))
    remarks = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String(32))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_by = db.Column(db.String(32))

    def __init__(self, ip_addr_list_id=None):
        self.ip_addr_list_id = ip_addr_list_id

    def getCmsCmsIpAddress(self, ip_addr_list_id, ip_address):
        return db.session.query(CmsIpAddrList).filter(CmsIpAddrList.ip_addr_list_id == ip_addr_list_id,
                                                      CmsIpAddrList.ip_address == ip_address).first()

    def getCmsIpAddrList(self, ip_addr_list_id):
        selectSql = '''
            SELECT C.IP_ADDR_LIST_ID, C.IP_ADDRESS, C.SUBNET_MASK, C.REMARKS,
                   C.IP_ADDRESS || ' - ' || PKG_IP_ADDR_UTIL.LAST_IP_ADDR(C.IP_ADDRESS, C.SUBNET_MASK) IP_ADDR_RANGE
              FROM CMS_IP_ADDR_LIST C
             WHERE C.IP_ADDR_LIST_ID = :ip_addr_list_id
             ORDER BY PKG_IP_ADDR_UTIL.INET_ATON(C.IP_ADDRESS)
        '''
        t = text(selectSql)
        rst = db.session.execute(t, {'ip_addr_list_id': ip_addr_list_id})

        dic, array = {}, []
        for rowproxy in rst:
            for column, val in rowproxy.items():
                value = '' if val is None else val
                if column == "remarks":
                    value = Markup(str(Markup.escape(value)).replace("\r\n", "</br>").replace(" ", "&nbsp;"))
                dic = {**dic, **{column: (value)}}
            array.append(dic)
        return array

    def addCmsIpAddr(self, cmsIpAddr, userId):
        cmsIpAddr.created_by = userId
        cmsIpAddr.created_at = datetime.now()
        cmsIpAddr.updated_by = userId
        cmsIpAddr.updated_at = datetime.now()
        return db.session.add(cmsIpAddr)

    def updateCmsIpAddr(self, cmsIpAddr, userId):
        cmsIpAddr.updated_by = userId
        cmsIpAddr.updated_at = datetime.now()
        return cmsIpAddr

    def delCmsIpAddr(self, ip_addr_list_id, ip_address):
        del_file = db.session.query(CmsIpAddrList).filter(CmsIpAddrList.ip_addr_list_id == ip_addr_list_id,
                                                          CmsIpAddrList.ip_address == ip_address).delete()
