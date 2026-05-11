import urllib.request, urllib.parse, re

# Fetch CSRF
req = urllib.request.Request('http://127.0.0.1:8000/')
resp = urllib.request.urlopen(req)
html = resp.read().decode()
m = re.search(r'name="csrfmiddlewaretoken" value="(.+?)"', html)
csrf = m.group(1) if m else ''
print('CSRF found:', csrf[:10] + '...')

# Test simplex with <=
post = {
    'csrfmiddlewaretoken': csrf,
    'num_vars': '2', 'num_cons': '2',
    'obj_coeff_0': '3', 'obj_coeff_1': '5',
    'mode': 'max', 'method': 'simplex',
    'constraint_0_0': '1', 'constraint_0_1': '2',
    'sign_0': '<=', 'rhs_0': '10',
    'constraint_1_0': '3', 'constraint_1_1': '2',
    'sign_1': '<=', 'rhs_1': '12'
}
body = urllib.parse.urlencode(post).encode()
req2 = urllib.request.Request('http://127.0.0.1:8000/solve/', data=body, method='POST')
req2.add_header('Content-Type', 'application/x-www-form-urlencoded')
req2.add_header('Referer', 'http://127.0.0.1:8000/')
resp2 = urllib.request.urlopen(req2)
html2 = resp2.read().decode()
print('Simplex <=: Status', resp2.status)
print('  Has Optimal:', 'Optimal Solution' in html2)
print('  Has Z value:', 'Z =' in html2)

# Test graphical
post['method'] = 'graphical'
body3 = urllib.parse.urlencode(post).encode()
req3 = urllib.request.Request('http://127.0.0.1:8000/solve/', data=body3, method='POST')
req3.add_header('Content-Type', 'application/x-www-form-urlencoded')
req3.add_header('Referer', 'http://127.0.0.1:8000/')
resp3 = urllib.request.urlopen(req3)
html3 = resp3.read().decode()
print('Graphical <=: Status', resp3.status)
print('  Has chart:', 'data:image/png' in html3)

# Test >=
post['sign_0'] = '>='
post['sign_1'] = '>='
post['method'] = 'simplex'
body4 = urllib.parse.urlencode(post).encode()
req4 = urllib.request.Request('http://127.0.0.1:8000/solve/', data=body4, method='POST')
req4.add_header('Content-Type', 'application/x-www-form-urlencoded')
req4.add_header('Referer', 'http://127.0.0.1:8000/')
resp4 = urllib.request.urlopen(req4)
html4 = resp4.read().decode()
print('Simplex >=: Status', resp4.status)
print('  Has Optimal:', 'Optimal Solution' in html4)

print('All tests done.')
