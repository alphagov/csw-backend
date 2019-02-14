from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import requests
import subprocess


def before_all(context):
    context.api_session = requests.Session()

    context.browser = webdriver.Firefox()


def after_all(context):
    context.browser.quit()


#def before_feature(context, feature):


#def after_feature(context, feature):

