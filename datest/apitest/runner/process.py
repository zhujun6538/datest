import json
import time

from zthttpfunc import ZTPostWithFunctions
from loguru import logger
from productor import Saver


class Callfunc(object):
    def manuel_process(self,testdata):
        # if testdata.get('before'):
        #     ZTPostWithFunctions(testdata['before']).test_start()
        #     time.sleep(2)
        ZTPostWithFunctions(testdata).test_start()

    def yb(self,testdata):
        testdata1 = testdata.copy()
        testdata2 = testdata.copy()
        testdata1['asserts'] = [['eq', 'body.resultCode', '00000'], ['eq', 'body.resultDesc', '成功']]
        ZTPostWithFunctions(testdata1).run()
        orderno = f"&$.{Saver.caseno}..orderNo&"
        testdata2['data'] = Saver.handle_params('{"orderNo":"%s"}' % (orderno))
        testdata2['url'] = testdata2['url'].replace('Apply', 'Result')
        issuc = False
        for i in range(3):
            time.sleep(2)
            issuc = ZTPostWithFunctions(testdata2).run()
            if issuc:
                break