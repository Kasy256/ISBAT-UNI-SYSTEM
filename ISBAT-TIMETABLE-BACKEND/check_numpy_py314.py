import json
import urllib.request

url = 'https://pypi.org/pypi/numpy/json'
with urllib.request.urlopen(url) as resp:
    data = json.load(resp)

versions = ['2.4.4', '2.3.5', '2.2.6', '2.1.3', '2.0.2', '1.26.4']
for ver in versions:
    print('===', ver)
    urls = data['releases'].get(ver, [])
    if not urls:
        print('missing')
        continue
    found = False
    for u in urls:
        if u['packagetype'] == 'bdist_wheel' and 'cp314' in u['filename']:
            print('wheel', u['filename'])
            found = True
    if not found:
        print('no cp314 wheels')
