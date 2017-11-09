'''
Created on Nov 9, 2017

@author: khoi.ngo
'''


def generate_random_string(prefix="", suffix="", length=20):
    """
    Generate random string .

    :param prefix: (optional) Prefix of a string.
    :param suffix: (optional) Suffix of a string.
    :param length: (optional) Max length of a string (exclude prefix and suffix)
    :return: The random string.
    """
    import random
    import string
    random_str = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))
    result = str(prefix) + random_str + str(suffix)
    return result
