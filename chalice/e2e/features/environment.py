from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import requests
import subprocess

def before_feature(context, feature):
    caps = {}
    caps['name'] = 'Behave Example'
    caps['build'] = '1.0'
    caps['browserName'] = "Chrome"      # pulls the latest version of Chrome by default
    caps['platform'] = "Windows 10"     # to specify a version, add caps['version'] = "desired version"
    caps['screen_resolution'] = '1366x768'
    caps['record_video'] = 'true'
    caps['record_network'] = 'true'
    caps['take_snapshot'] = 'true'


    context.api_session = requests.Session()

    # cmd = "cbt_tunnels --username " + username + " --authkey " + authkey + " --ready tunnel_ready asadmin"

    # context.tunnel_proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)



    context.browser = webdriver.Firefox()
    # context.browser = webdriver.Remote(
    #     desired_capabilities=caps,
    #     command_executor="http://www.google.com"
    # )

def after_feature(context, feature):
    context.browser.quit()
    # subprocess.Popen.terminate(context.tunnel_proc)