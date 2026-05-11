import requests, re

s = requests.Session()
r = s.get('http://127.0.0.1:8000/')
token = re.search(r'value="(.+?)"', r.text).group(1)

data = {
    'csrfmiddlewaretoken': token,
    'num_vars': '2',
    'num_cons': '2',
    'obj_coeff_0': '3',
    'obj_coeff_1': '5',
    'constraint_0_0': '1',
    'constraint_0_1': '2',
    'rhs_0': '10',
    'constraint_1_0': '3',
    'constraint_1_1': '2',
    'rhs_1': '12',
    'method': 'simplex'
}

resp = s.post('http://127.0.0.1:8000/solve/', data=data)
title = re.search(r'<title>(.+?)</title>', resp.text)
print('Status:', resp.status_code)
print('Title:', title.group(1) if title else 'NO TITLE')
print('Contains Simplex:', 'Simplex' in resp.text)
print('Contains Graphical:', 'Graphical' in resp.text)
