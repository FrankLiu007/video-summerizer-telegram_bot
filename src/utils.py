import urllib3
import os
import json
def get_http_responce(url, method, params):

    http = urllib3.ProxyManager(
        os.environ["HTTPS_PROXY"],
        retries=urllib3.Retry(int(os.environ["https_request_retry"]))
    )

    response = http.request(method, url, fields=params)
    http.clear()
    return response