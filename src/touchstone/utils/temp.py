def id_dict(obj):
    return obj.__class__.__name__ == 'dict'


def _contains_key_rec(v_key, v_dict):
    for curKey in v_dict:
        if curKey == v_key or (id_dict(v_dict[curKey]) and _contains_key_rec(v_key, v_dict[curKey])):
            return True
    return False


def _get_value_rec(v_key, v_dict):
    for curKey in v_dict:
        if curKey == v_key:
            return v_dict[curKey]
        elif id_dict(v_dict[curKey]) and _get_value_rec(v_key, v_dict[curKey]):
            return _contains_key_rec(v_key, v_dict[curKey])
    return None

def compare_dict(d1, d2, aggs, _message, buckets):
    for key in d1:
        if _contains_key_rec(key, d2):
            d2_value = _get_value_rec(key, d2)
            #if isinstance(d1[key],dict) and isinstance(d2_value,dict):
            if type(d1[key]) is dict and type(d2_value) is dict:
                print("if case")
                if key not in aggs and key not in buckets:
                    print(key)
                    _message = _message + "| {:20} ".format(key)
                compare_dict(d1[key],d2_value,aggs,"",buckets)
            else:
                print("else case")
                print("unequal values")
                print("values are as follows: \n"
                      "list1: " + str(d1[key]) + "\n" +
                      "list2: " + str(d2_value))
                print("================================================================================================================================")
        else:
            print("dict d2 does not contain key: " + str(key))
