from behave import given, when, then
import time
import os

@when('you navigate to CSW homepage')
def step(context):
    url = os.environ['CSW_URL']
    context.browser.get(url)

@when('you navigate to CSW page "{path}"')
def step(context, path):
    url = os.environ['CSW_URL'] + path
    print(url)
    context.browser.get(url)

@when('you login to CSW')
def step(context):
    creds = {
        'email': os.environ['CSW_USER'] + '@digital.cabinet-office.gov.uk',
        'client': os.environ['CSW_CLIENT'],
        'secret': os.environ['CSW_SECRET']
    }
    url = os.environ['CSW_URL']
    url = url + 'temp-login?client=' + creds['client'] + '&secret=' + creds['secret'] + '&email=' + creds['email']
    response = context.browser.get(url)

    # context.api_session.headers.update({'x-test': 'true'})
    print(response)

@then('the content of element with selector "{selector}" equals "{title}"')
def step(context, selector, title):
    elem = context.browser.find_element_by_css_selector(selector).text
    print(elem)
    assert elem == title

@given('the credentials')
def step(context):
    context.browser.header_overrides = {
        'Client': os.environ['CSW_CLIENT'],
        'Secret': os.environ['CSW_SECRET']
    }
    print(str(context.browser.header_overrides))


@when('login post to "{url}"')
def step(context, url):
    creds = {
        'email':  os.environ['CSW_USER']+'@digital.cabinet-office.gov.uk',
        'client': os.environ['CSW_CLIENT'],
        'secret': os.environ['CSW_SECRET']
    }
    url = url + '?client='+creds['client']+'&secret='+creds['secret']+'&email='+creds['email']
    response = context.browser.get(url)

    #context.api_session.headers.update({'x-test': 'true'})
    print(response)

@then('wait "{seconds}" seconds')
def step(context, seconds):
    time.sleep(int(seconds))