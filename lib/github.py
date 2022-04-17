import json

import requests


def github():
    api_url = "https://api.github.com"
    api_token = 'your_token_goes_here'

    # form a request URL
    url = api_url + "/gists"
    print
    "Request URL: %s" % url

    # print headers,parameters,payload
    headers = {'Authorization': 'token %s' % api_token}
    params = {'scope': 'gist'}
    payload = {"description": "GIST created by python code", "public": True, "files": {"python request module": {
        "content": "Python requests has 3 parameters: 1)Request URL\n 2)Header Fields\n 3)Parameter \n4)Request body"}}}

    # make a requests
    res = requests.post(url, headers=headers, params=params, data=json.dumps(payload))

    # print response --> JSON
    print
    res.status_code
    print
    res.url
    print
    res.text
    j = json.loads(res.text)

    # Print created GIST's details
    for gist in range(len(j)):
        print
        "Gist URL : %s" % (j['url'])
        print
        "GIST ID: %s" % (j['id'])