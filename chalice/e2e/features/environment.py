from selenium import webdriver
import requests


def before_all(context):
    context.api_session = requests.Session()

    context.browser = webdriver.Firefox()


def after_all(context):
    context.browser.quit()


#def before_feature(context, feature):


#def after_feature(context, feature):

