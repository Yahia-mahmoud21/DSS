import urllib.request, urllib.parse, re

req = urllib.request.Request('http://127.0.0.1:8000/')
resp = urllib.request.urlopen(req)
cookies = resp.headers.get('Set-Cookie', '')
csrf = re.search(r'csrftoken=(\w+)', cookies).group(1)
resp.read()

data = urllib.parse.urlencode({
    'csrfmiddlewaretoken': csrf,
    'num_vars': '2', 'num_cons': '2',
    'obj_coeff_0': '3', 'obj_coeff_1': '5',
    'constraint_0_0': '1', 'constraint_0_1': '2', 'rhs_0': '10',
    'constraint_1_0': '3', 'constraint_1_1': '2', 'rhs_1': '12',
    'mode': 'max', 'method': 'simplex'
}).encode()

req2 = urllib.request.Request('http://127.0.0.1:8000/solve/', data=data, method='POST')
req2.add_header('Cookie', 'csrftoken=' + csrf)
req2.add_header('Content-Type', 'application/x-www-form-urlencoded')

try:
    resp2 = urllib.request.urlopen(req2)
    print('OK:', resp2.status)
except urllib.error.HTTPError as e:
    print('ERROR:', e.code)
    body = e.read().decode()
    m = re.search(r'Exception Value:</th><td>(.+?)</td>', body)
    if m:
        print('Exception:', m.group(1).strip())
    else:
        # Try alternative pattern
        m2 = re.search(r'class="exception_value"[^>]*>(.+?)</pre>', body, re.DOTALL)
        if m2:
            print('Exception:', m2.group(1).strip())
        else:
            print('Body:', body[:1500])
