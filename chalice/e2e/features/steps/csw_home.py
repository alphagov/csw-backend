from behave import given, when, then
import time

@then('header with class "{selector}" equals "{title}"')
def step(context, selector, title):
    elem = context.browser.find_element_by_class_name(selector)
    assert elem == title


