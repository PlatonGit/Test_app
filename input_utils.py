import re
from custom_exceptions import (UserInputTextException, UserInputNumException)


def raw_input(string):
    result = input(string)
    
    if len(re.findall(r'[^ \#\^\(\)\%\*\'\-\?\,\.\;\+\=\w\d]', result)):
        raise UserInputTextException
    return result


def raw_num_input(string):
    result = input(string)

    if len(re.findall(r'[^\d]', result)):
        raise UserInputNumException
    return result


def get_input_function():
    try:
        input_function = raw_input
    except NameError:
        input_function = input

    return input_function


def get_num_input_function():
    try:
        input_function = raw_num_input
    except NameError:
        input_function = input
    
    return input_function