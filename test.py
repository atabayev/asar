import os


def get_conf(key):
    if not os.path.exists('serv_cfg'):
        return '0'
    with open('serv_cfg', 'r') as fl:
        for line in fl:
            k, v = line.split()
            if k == key:
                return v
    return '0'


def save_conf(key, value):
    if not os.path.exists('serv_cfg'):
        with open('serv_cfg', 'w') as fl:
            fl.write(key + ' ' + value)
    else:
        with open('serv_cfg', 'r') as fl:
            for line in fl:
                res = fl.read()
        ind = res.find(key)




get_conf('grab')
