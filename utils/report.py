'''
Created on Nov 9, 2017

@author: nhan.nguyen
'''

import json
import time
import os


class KeyWord:
    TEST_CASE = "testcase"
    RESULT = "result"
    START_TIME = "starttime"
    DURATION = "duration"
    RUN = "run"
    STEP = "step"
    STATUS = "status"
    MESSAGE = "message"


class Status:
    PASSED = "Passed"
    FAILED = "Failed"


class TestReport:
    __default_result_dir = os.path.join(os.path.dirname(__file__), "..") + "/test_results/"
    __result_dir = os.path.join(os.path.dirname(__file__), "..") + "/test_results/"

    def __init__(self, test_case_name):
        self.__error_id = 1
        self.__test_result = {}
        self.__run = []
        self.__test_result[KeyWord.TEST_CASE] = test_case_name
        self.__test_result[KeyWord.RESULT] = Status.PASSED
        self.__test_result[KeyWord.START_TIME] = str(time.strftime("%Y%m%d_%H-%M-%S"))

    def set_result(self, result):
        self.__test_result[KeyWord.RESULT] = result

    def set_duration(self, duration):
        self.__test_result[KeyWord.DURATION] = round(duration * 1000)

    def set_step_status(self, step_summary: str, status: str = Status.PASSED, message: str = None):
        temp = {KeyWord.STEP: step_summary, KeyWord.STATUS: status, KeyWord.MESSAGE: message}
        self.__run.append(temp)

    def write_result_to_file(self):
        temp_dir = self.__create_result_folder()
        filename = "{0}/{1}_{2}.json".format(temp_dir, self.__test_result[KeyWord.TEST_CASE],
                                             self.__test_result[KeyWord.START_TIME])
        self.__test_result[KeyWord.RUN] = self.__run
        with open(filename, "w+") as outfile:
            json.dump(self.__test_result, outfile, ensure_ascii=False, indent=2)

    def set_test_failed(self):
        self.set_result(Status.FAILED)

    def set_test_passed(self):
        self.set_test_passed(Status.PASSED)

    def __create_result_folder(self):
        temp_dir = self.__result_dir
        if self.__result_dir == TestReport.__default_result_dir:
            temp_dir = "{0}{1}_{2}".format(temp_dir, self.__test_result[KeyWord.TEST_CASE],
                                           self.__test_result[KeyWord.START_TIME])
        if not os.path.exists(temp_dir):
            try:
                os.makedirs(temp_dir)
            except IOError as E:
                print(str(E))
                raise E

        return temp_dir

    @staticmethod
    def change_result_dir(new_dir: str):
        if not new_dir.endswith("/"):
            new_dir += "/"
        TestReport.result_dir = new_dir
