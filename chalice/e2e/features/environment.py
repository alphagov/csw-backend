from selenium import webdriver
import os
import requests


def before_all(context):
    context.api_session = requests.Session()
    options = webdriver.FirefoxOptions()
    options.headless = (os.environ['CSW_E2E_HEADLESS'] == "true")
    context.browser = webdriver.Firefox(options=options)


def after_all(context):
    context.browser.quit()


#def before_feature(context, feature):


#def after_feature(context, feature):

