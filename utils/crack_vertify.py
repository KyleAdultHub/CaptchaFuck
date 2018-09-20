# coding:utf-8
import requests
from hashlib import md5


class RClient(object):
    def __init__(self, username, password, soft_id, soft_key):
        self.username = username
        self.password = md5(password).hexdigest()
        self.soft_id = soft_id
        self.soft_key = soft_key
        self.base_params = {
            'username': self.username,
            'password': self.password,
            'softid': self.soft_id,
            'softkey': self.soft_key,
        }
        self.headers = {
            'Connection': 'Keep-Alive',
            'Expect': '100-continue',
            'User-Agent': 'ben',
        }

    def rk_create(self, im, im_type, timeout=20):
        """
        im: 图片字节
        im_type: 题目类型
        """
        params = {
            'typeid': im_type,
            'timeout': timeout,
        }
        params.update(self.base_params)
        files = {'image': ('a.jpg', im)}
        try:
            r = requests.post('http://api.ruokuai.com/create.json', data=params, files=files, headers=self.headers)
        except:
            return {'Result': 'aaaa', 'Id': None}
        return r.json()

    def rk_report_error(self, im_id):
        """
        im_id:报错题目的ID
        """
        params = {
            'id': im_id,
        }
        params.update(self.base_params)
        r = requests.post('http://api.ruokuai.com/reporterror.json', data=params, headers=self.headers, timeout=20)
        return r.json()


class DoCrack(object):
    def __init__(self):
        self.rc = RClient('OriginDong'.encode(), '!QAZ2wsx'.encode(), '1'.encode(),
                          'b40ffbee5c1cf4e38028c197eb2fc751'.encode())

    def do_crack(self, im):
        """
        Get img_str
        params: im(bytes)
        return: dict:status, img_str
        """
        img_req = self.rc.rk_create(im, 3050)
        img_str = img_req.get('Result')
        img_id = img_req.get('Id')
        status = 0
        crack_success = False
        if img_str:
            status = 200
            crack_success = True
        return {'status': status, 'img_str': img_str, 'img_id': img_id, 'crack_success': crack_success}

    def report_error(self, img_id):
        self.rc.rk_report_error(img_id)


if __name__ == '__main__':
    with open(r'G:\kyle.Liu\working_code\crawler\UncreditExecutor\test.png', 'rb') as f:
        im = f.read()
    f.close()

    dc = DoCrack()
    res = dc.do_crack(im)
    print(res)
    pass
