import os
import time
import allure
import pytest
from zthttpfunc import ZTPostWithFunctions
from productor import *
from process import *

filepath = os.path.dirname(__file__)


class Test_Openapi(object):
    @pytest.mark.work
    def test_api(self, testdata):
        allure.dynamic.feature(testdata['suitename'])
        allure.dynamic.story(testdata['group'])
        allure.dynamic.title(testdata['casename'])
        Callfunc().__getattribute__(testdata['callfunc'])(testdata)



# if __name__=="__main__":
#     pytest.main(['-v'])



