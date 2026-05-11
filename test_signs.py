import urllib.request, urllib.parse, re

def get_csrf():
    req = urllib.request.Request('http://127.0.0.1:8000/')
    resp = urllib.request.urlopen(req)
    cookies = resp.headers.get('Set-Cookie', '')
    m = re.search(r'csrftoken=([\w-]+)', cookies)
    if m:
        return m.group(1)
    html = resp.read().decode()
    m2 = re.search(r'name="csrfmiddlewaretoken" value="(.+?)"', html)
    return m2.group(1) if m2 else ''

def test_case(name, post_data):
    csrf = get_csrf()
    post_data['csrfmiddlewaretoken'] = csrf
    body = urllib.parse.urlencode(post_data).encode()
    req = urllib.request.Request('http://127.0.0.1:8000/solve/', data=body, method='POST')
    req.add_header('Cookie', 'csrftoken=' + csrf)
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')
    resp = urllib.request.urlopen(req)
    html = resp.read().decode()
    print(f"{name}: Status={resp.status}")
    print(f"  Has Optimal: {'Optimal Solution' in html}")
    print(f"  Has signs: {'&le;' in html or '&ge;' in html}")
    return html

base_post = {
    'num_vars': '2', 'num_cons': '2',
    'obj_coeff_0': '3', 'obj_coeff_1': '5',
    'mode': 'max', 'method': 'simplex',
    'constraint_0_0': '1', 'constraint_0_1': '2', 'rhs_0': '10',
    'constraint_1_0': '3', 'constraint_1_1': '2', 'rhs_1': '12',
}

# Test <=
post1 = dict(base_post)
post1.update({'sign_0': '<=', 'sign_1': '<='})
test_case('<= constraints', post1)

# Test >=
post2 = dict(base_post)
post2.update({'sign_0': '>=', 'sign_1': '>='})
test_case('>= constraints', post2)

# Test =
post3 = dict(base_post)
post3.update({'sign_0': '=', 'sign_1': '='})
test_case('= constraints', post3)

# Test graphical with <=
post4 = dict(base_post)
post4.update({'sign_0': '<=', 'sign_1': '<=', 'method': 'graphical'})
test_case('graphical <=', post4)

# Test min mode
post5 = dict(base_post)
post5.update({'sign_0': '<=', 'sign_1': '<=', 'mode': 'min'})
test_case('min <=', post5)

print('All tests done.')
