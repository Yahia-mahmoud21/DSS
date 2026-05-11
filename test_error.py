import urllib.request, urllib.parse, re

req = urllib.request.Request('http://127.0.0.1:8000/')
resp = urllib.request.urlopen(req)
html = resp.read().decode()
m = re.search(r'name="csrfmiddlewaretoken" value="(.+?)"', html)
csrf = m.group(1)

post = {
    'csrfmiddlewaretoken': csrf,
    'num_vars': '2', 'num_cons': '2',
    'obj_coeff_0': '3', 'obj_coeff_1': '5',
    'mode': 'max', 'method': 'simplex',
    'constraint_0_0': '1', 'constraint_0_1': '2', 'sign_0': '<=', 'rhs_0': '10',
    'constraint_1_0': '3', 'constraint_1_1': '2', 'sign_1': '<=', 'rhs_1': '12'
}
body = urllib.parse.urlencode(post).encode()
req2 = urllib.request.Request('http://127.0.0.1:8000/solve/', data=body, method='POST')
req2.add_header('Content-Type', 'application/x-www-form-urlencoded')
req2.add_header('Referer', 'http://127.0.0.1:8000/')

try:
    resp2 = urllib.request.urlopen(req2)
    print('OK', resp2.status)
except urllib.error.HTTPError as e:
    body = e.read().decode()
    m2 = re.search(r'Exception Value:</th><td>(.+?)</td>', body, re.DOTALL)
    if m2:
        print('Exception:', m2.group(1).strip())
    else:
        print('Status:', e.code)
        print('Body:', body[:600])
