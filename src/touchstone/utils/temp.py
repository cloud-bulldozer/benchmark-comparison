import logging


_logger = logging.getLogger("touchstone")


def id_dict(obj):
    return obj.__class__.__name__ == 'dict'


def _contains_key_rec(v_key, v_dict):
    for curKey in v_dict:
        if curKey == v_key or \
            (id_dict(v_dict[curKey]) and
             _contains_key_rec(v_key, v_dict[curKey])):
            return True
    return False


def _get_value_rec(v_key, v_dict):
    for curKey in v_dict:
        if curKey == v_key:
            return v_dict[curKey]
        elif id_dict(v_dict[curKey]) and _get_value_rec(v_key, v_dict[curKey]):
            return _contains_key_rec(v_key, v_dict[curKey])
    return None


def _print_comparison(entry1, entry2, uuid1, uuid2, _message, key):
    _header = _message + "{:20} | ".format("uuid")
    if type(entry1) is dict and type(entry2) is dict:
        _message1 = "{:20} | ".format(uuid1)
        _message2 = "{:20} | ".format(uuid2)
        for _key in entry1:
            _string = str(key) + '({})'.format(_key)
            _header = _header + "{:20} | ".format(_string)
            _message1 = _message1 + " {:20} | ".format(str(entry1[_key]))
            _message2 = _message2 + " {:20} | ".format(str(entry2[_key]))
        print(_header)
        print(_message1)
        print(_message2)
    else:
        _header = _header + "{:20} | ".format(key)
        print(_header)
        _message1 = "{:20} | ".format(uuid1)
        _message1 = _message1 + " {:20} | ".format(str(entry1))
        print(_message1)
        _message2 = "{:20} | ".format(uuid2)
        _message2 = _message2 + " {:20} | ".format(str(entry2))
        print(_message2)


def compare_dict(d1, d2, aggs, _message, buckets, uuid1, uuid2, _header):
    for key in d1:
        if _contains_key_rec(key, d2):
            d2_value = _get_value_rec(key, d2)
            if type(d1[key]) is dict and type(d2_value) is dict and \
                key not in aggs:
                if key not in aggs and key not in buckets:
                    _message = _message + " {:20} |".format(key)
                compare_dict(d1[key], d2_value, aggs, _message, buckets,
                             uuid1, uuid2, _header)
            elif key in aggs:
                print(_header)
                print(_message)
                _print_comparison(d1[key], d2_value, uuid1, uuid2, "", key)
                print("=" * 128)
        else:
            _logger.debug("dict d2 does not contain key: " + str(key))
