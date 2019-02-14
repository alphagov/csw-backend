from behave import given, when, then
import time
import os

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