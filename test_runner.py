import urllib.request, urllib.parse, re

def fetch_csrf():
    req = urllib.request.Request('http://127.0.0.1:8000/')
    resp = urllib.request.urlopen(req)
    html = resp.read().decode()
    m = re.search(r'name="csrfmiddlewaretoken" value="(.+?)"', html)
    return m.group(1) if m else ''

def test_post(data):
    csrf = fetch_csrf()
    data['csrfmiddlewaretoken'] = csrf
    body = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request('http://127.0.0.1:8000/solve/', data=body, method='POST')
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')
    req.add_header('Referer', 'http://127.0.0.1:8000/')
    resp = urllib.request.urlopen(req)
    return resp.status, resp.read().decode()

base = {
    'num_vars': '2', 'num_cons': '2',
    'obj_coeff_0': '3', 'obj_coeff_1': '5',
    'mode': 'max', 'method': 'simplex',
    'constraint_0_0': '1', 'constraint_0_1': '2', 'rhs_0': '10',
    'constraint_1_0': '3', 'constraint_1_1': '2', 'rhs_1': '12',
}

# Test 1: <=
d1 = dict(base)
d1.update({'sign_0': '<=', 'sign_1': '<='})
status, html = test_post(d1)
print('Test <=: status=' + str(status))
print('  optimal:', 'Optimal Solution' in html)
print('  sign_le:', '&le;' in html)

# Test 2: >=
d2 = dict(base)
d2.update({'sign_0': '>=', 'sign_1': '>='})
status, html = test_post(d2)
print('Test >=: status=' + str(status))
print('  optimal:', 'Optimal Solution' in html)
print('  sign_ge:', '&ge;' in html)

# Test 3: =
d3 = dict(base)
d3.update({'sign_0': '=', 'sign_1': '='})
status, html = test_post(d3)
print('Test =: status=' + str(status))
print('  optimal:', 'Optimal Solution' in html)
print('  sign_eq:', '=&nbsp;' in html or '= ' in html)

# Test 4: graphical
d4 = dict(base)
d4.update({'sign_0': '<=', 'sign_1': '<=', 'method': 'graphical'})
status, html = test_post(d4)
print('Test graphical: status=' + str(status))
print('  chart:', 'data:image/png' in html)

print('Done.')
