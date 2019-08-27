import requests
import json

URL = 'http://127.0.0.1:5000/array/search/binary/'
t_array = [1,3,5,8,10,12]
elem_in_array = 8

request_data = {
    'search_array': t_array, 
    'search_element': elem_in_array
}
post_data = json.dumps(request_data)
resp = requests.post(URL, json=post_data)

if resp.ok:
    print("Result:\n",resp.text, sep='')
else:
    print("Could not get result:\n",resp.text, sep='')