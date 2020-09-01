from datetime import datetime
from time import sleep
import yaml
import os
import time
from os.path import dirname
import logging
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as expCond
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementNotVisibleException
from selenium.common.exceptions import ElementNotSelectableException
from selenium.common.exceptions import ElementClickInterceptedException


# log configuration
logging.basicConfig(filename='debug.log',
                    level=logging.DEBUG, format='%(asctime)s %(message)s')

# read config file


def read_yaml(config_file_path):
    yaml_contents = yaml.load(
        open(config_file_path), Loader=yaml.FullLoader)
    return yaml_contents


class Actions:
    """Class which holds all the actions required to perform in a test
    """

    def __init__(self):
        pass

    def launch_browser(self, browser):
        """Function to launch a specific browser

        Args:
            browser (str): Browser type string

        Returns:
            object: driver
        """
        dir_path = dirname(dirname(os.getcwd()))
        chromedriver_path = dir_path+r'\\drivers\\chromedriver.exe'
        geckodriver_path = dir_path+r'\drivers\geckodriver.exe'
        try:
            if browser.lower() == 'chrome':
                driver = webdriver.Chrome(
                    executable_path=chromedriver_path)
            elif browser.lower() == 'firefox':
                driver = webdriver.Firefox(
                    executable_path=geckodriver_path)
                # TODO
            elif browser.lower() == 'ie':
                pass
                # TODO
            else:
                pass
                # TODO
            driver.delete_all_cookies()
            logging.info("Browser launched : ")
            return driver
        except Exception as e:
            logging.error(e)
            print("Exception launch browser: ", e)

    def input_value(self, _element, test_data):
        """Function to input a value in a text field

        Args:
            driver (object): webdriver object
            obj_prop (str): object property

        Returns:
            str: result of the input action
        """
        try:
            _element.clear()
            _element.send_keys(test_data)
            return "pass"
        except Exception as e:
            print('Exception occured while input: ', e)
            return "fail"

    def click(self, _element):
        """Function to click on an element

        Args:
            _element (object): Web element

        Returns:
            str: result of click action
        """
        try:
            _element.click()
            return "pass"
        except Exception as e:
            logging.error(e)
            print('Exception occured while click: ', e)
            return "fail"

    def wait(self, test_data):
        """Function to wait for a period of time

        Args:
            test_data (str): time to wait

        Returns:
            str: Result of wait action
        """
        try:
            sleep(int(test_data))
            return "pass"
        except Exception as e:
            logging.error(e)
            print('Exception occured while wait: ', e)
            return "fail"

    def text(self, _element, test_data):
        """Function to verify the text of an element

        Args:
            _element (obj): web element
            test_data (str): value to compare with

        Returns:
            str: result of the text function
        """
        try:
            temp_text = _element.text
            if(temp_text == test_data):
                return "pass"
            else:
                return "fail"
        except Exception as e:
            logging.error(e)
            print("Exception in text")
            return "fail"

    def close(self, driver):
        """Function to close the browser

        Args:
            driver (obj): web driver

        Returns:
            str: Result of the close browser action
        """
        try:
            driver.quit()
            return "pass"
        except Exception as e:
            logging.error(e)
            print("Exception whil closeing the browser: ", e)
            return "fail"


class Start_Execution(Actions):
    """Class to start test script execution

    Args:
        Actions (class): Actions class
    """

    def __init__(self, _paths, browser):
        self._paths = _paths
        self.browser = browser

    # Collect Test Scripts

    def collect_test_scripts(self, test_scripts_fpath):
        """Function to collect all the test scripts in a folder

        Args:
            test_scripts_fpath (str): test scripts folder path

        Returns:
            list: list of test scripts
        """
        _scripts = os.listdir(test_scripts_fpath)
        return _scripts

    # Read Test Script
    def read_test_script(self, test_script_path):
        """Function to read the test script

        Args:
            test_script_path (str): path of the test script

        Returns:
            str: test script name
            str: test steps
        """
        actions = yaml.load(open(test_script_path), Loader=yaml.FullLoader)
        name = actions['name']
        steps = actions['steps']
        return name, steps

    # Wrtie test_script result
    def write_test_script_result(self, filename, test_scripts_result):
        """Wite test results to Yaml file

        Args:
            filename (str): path to create file and file name
            test_scripts_result (obj): test scripts results object
        """
        with open(filename, 'w') as result:
            yaml.dump(test_scripts_result, result)

    # get Test Element
    def get_test_element(self, driver, test_element):
        """Function to get the test element property

        Args:
            driver (obj): webdriver
            test_element (str): web element on which an action to be performed

        Returns:
            str: element
        """
        try:
            test_element = test_element.strip('\"')
            driver_wait = WebDriverWait(driver, 100, poll_frequency=1,
                                        ignored_exceptions=[
                                            ElementNotVisibleException,
                                            ElementNotSelectableException,
                                            ElementClickInterceptedException])
            if test_element.startswith('#'):
                test_element = test_element.lstrip('#')
                element = driver_wait.until(
                    expCond.presence_of_element_located((By.ID, test_element)))
            elif test_element.startswith(('//', '/')):
                element = driver_wait.until(
                    expCond.presence_of_element_located(
                        (By.XPATH, test_element)))
            elif test_element.startswith('.'):
                test_element = test_element.lstrip('.')
                element = driver_wait.until(
                    expCond.presence_of_element_located
                    ((By.CLASS_NAME, test_element)))
            else:
                element = driver_wait.until(
                    expCond.presence_of_element_located
                    ((By.LINK_TEXT, test_element)))
            return element
        except Exception as e:
            print("Exception occurred in get_test_element: ", test_element, e)

    def open_application(self, driver, app_url):
        """Function to open the application in the browser

        Args:
            driver (obj): webdriver
            app_url (str): application url

        Returns:
            str: result of the function execution
        """
        try:
            driver.maximize_window()
            driver.get(app_url)
            return "pass"
        except Exception as e:
            print("Exception occurred while opening application: ", e)
            return "fail"

    # Execute test step
    def execute_test_step(self, driver, action, test_element, test_data):
        """ Function to execute a test step

        Args:
            driver (obj): Webdriver
            action (str): Action to perform on a test element
            test_element (str): Element on which an action to be performed
            test_data (str): test data required while performing an action

        Returns:
            [type]: [description]
        """
        try:
            action_result = ""
            action = action.lower()
            if action == "launch":
                action_result = self.open_application(driver, test_data)
            elif action == "input":
                action_result = self.input_value(test_element, test_data)
            elif action == "click":
                action_result = self.click(test_element)
            elif action == "wait":
                action_result = self.wait(test_data)
            elif action == "text":
                action_result = self.text(test_element, test_data)
            elif action == "close":
                action_result = self.close(driver)
            else:
                print("Action does not exsit, please check")
                action_result = "fail"
            return action_result
        except Exception as e:
            print("error occured in execute_test_step: ", e)
            return "fail"

    # Start Execution

    def start_execution(self):
        """ To start test scripts execution

        Args: No args

        Returns:
            No Returns
        """
        # collect Test Scripts
        test_scripts = self.collect_test_scripts(
            self._paths['test_scripts_path'])

        # Test Script results
        test_scripts_result = []

        # Read each Test Script
        for test_script in test_scripts:
            startTime = time.time()
            test_script_path = self._paths['test_scripts_path']+'/'+test_script
            test_script_name, test_steps = self. read_test_script(
                test_script_path)
            driver = self.launch_browser(self.browser)
            # Test Script results
            test_script_result = {
                "Test Script": test_script_name, "test_steps_result": []}
            # Loop through steps
            test_steps_result = []
            res_flag = 0
            for test_step in test_steps:
                step_startTime = time.time()
                split_step = test_step.split(" ")
                action = split_step[0]
                test_element = split_step[1]
                if test_element != 'NA':
                    _element = self.get_test_element(driver, test_element)
                else:
                    _element = 'NA'
                test_data = split_step[2]
                test_step_result = self.execute_test_step(
                    driver, action, _element, test_data)
                step_endTime = time.time()
                if(test_step_result.lower() == "fail"):
                    res_flag = 1
                temp_result = {
                    "Test Step": test_step,
                    "Test Step Result": test_step_result,
                    "duration(sec)": step_endTime - step_startTime}
                test_steps_result.append(temp_result)
            test_script_result['test_steps_result'] = test_steps_result
            if res_flag == 1:
                test_script_result['result'] = "Fail"
            else:
                test_script_result['result'] = 'Pass'
            test_scripts_result.append(test_script_result)
            endTime = time.time()
            test_script_result['duration(sec)'] = endTime - startTime
        # test results file name
        res_filename = r'\results_'+str(datetime.now())+'.yaml'
        res_filename = res_filename.replace(":", "-")
        test_results_path = self._paths['test_results_path'] + res_filename
        # write test results to yaml file
        self.write_test_script_result(test_results_path, test_scripts_result)


if __name__ == "__main__":

    dir_path = dirname(dirname(os.getcwd()))

    # config_file_path
    config_file_path = dir_path+r'\\config.yaml'
    exec_params = read_yaml(config_file_path)

    home_path = dirname(dirname(dirname(os.getcwd())))

    # Browsers
    browser = exec_params['browser']

    # folder paths
    test_scripts_path = home_path+r'\test scripts'
    test_results_path = home_path+r'\test results'

    # create test scripts results directory
    try:
        os.makedirs(test_results_path)
    except OSError:
        print("results directory exists")

    folder_paths = {'test_scripts_path': test_scripts_path,
                    'test_results_path': test_results_path}

    # Initiate Execution
    execution = Start_Execution(folder_paths, browser)
    execution.start_execution()

    # yaml_contents = yaml.load(
    #     open("D:\\Work\\Automation\\gramenertest\\test scripts\\test1.yaml"), Loader=yaml.FullLoader)
    # print(yaml_contents['steps'][0].split(','))
