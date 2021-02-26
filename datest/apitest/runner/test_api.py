import os

import allure
import pytest

from httprequest import *

from productor import Saver

filepath = os.path.dirname(__file__)


class Test_Openapi(object):
    def test_openapi(self,testdata):
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



if __name__=="__main__":
    pytest.main(['-v'])



