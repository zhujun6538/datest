import os
import time

import allure
import pytest

from httprequest import *
from zthttpfunc import ZTPostWithFunctions
from productor import Saver

filepath = os.path.dirname(__file__)


class Test_Openapi(object):
    def test_general(self,testdata):
        Saver.caseno = testdata['caseno']
        allure.dynamic.feature(testdata['suitename'])
        allure.dynamic.story(testdata['group'])
        allure.dynamic.title(testdata['casename'])
        if testdata['method'] == 'POST':
            TestCasePostWithFunctions(testdata).test_start()
        elif testdata['method'] == 'GET':
            TestCaseGetWithFunctions(testdata).test_start()
        elif testdata['method'] == 'DELETE':
            TestCaseDeleteWithFunctions(testdata).test_start()

    @pytest.mark.work
    def test_ztapi(self, testdata):
        allure.dynamic.feature(testdata['suitename'])
        allure.dynamic.story(testdata['group'])
        allure.dynamic.title(testdata['casename'])
        if testdata.get('before'):
            ZTPostWithFunctions(testdata['before']).test_start()
            time.sleep(3)
        ZTPostWithFunctions(testdata).test_start()


# if __name__=="__main__":
#     pytest.main(['-v'])



