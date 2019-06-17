from behave import *
import requests
import os
import re


@when('you make an unauthenticated http get request to "{path}"')
def step(context, path):
    """
    This is separate from the 'you navigate to page' call because it uses requests.get
    instead of browser.get to get the JSON response.
    """
    context.url = os.environ["CSW_URL"] + path
    context.res = requests.get(context.url)


@when('you make an authenticated http get request to "{path}"')
def step(context, path):
    """
    This is separate from the 'you navigate to page' call because it uses requests.get
    instead of browser.get to get the JSON response.
    """
    context.url = os.environ["CSW_URL"] + path
    cookie = context.browser.get_cookie("session")
    token = cookie["value"]
    cookie_dict = {"session": token}
    context.res = requests.get(context.url, cookies=cookie_dict)


@then('response code is "{code}"')
def step(context, code):
    print("status code: " + str(context.res.status_code))
    assert str(context.res.status_code) == str(code)


@then('response mime type is "{mime_type}"')
def step(context, mime_type):
    print("mime type: " + str(context.res.headers["content-type"]))
    assert str(context.res.headers["content-type"]) == str(mime_type)


@then("body is valid json")
def step(context):
    is_json = False
    try:
        context.json = context.res.json()
        is_json = True
    except Exception as err:
        print("Error: " + str(err))
    assert is_json == True


def get_item_by_path(item, path):
    indexes = path.split(".")
    indexes.reverse()
    while len(indexes) > 0:
        path = indexes.pop()
        if re.match("^\d+$", path):
            item = item[int(path)]
        else:
            item = item[path]
    return item


@then('"{path}" exists and has datatype "{data_type}"')
def step(context, path, data_type):
    item = get_item_by_path(context.json, path)
    assert type(item).__name__ == data_type


@then('"{path}" exists and has value "{value}"')
def step(context, path, value):
    item = get_item_by_path(context.json, path)
    assert item == value


@then('"{path}" exists and matches pattern "{pattern}"')
def step(context, path, pattern):
    item = get_item_by_path(context.json, path)
    assert re.match(pattern, item)
