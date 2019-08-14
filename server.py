import copy
from datetime import datetime
import json

from flask import Flask,request
import pika

app = Flask(__name__)   

@app.route('/array/search/binary/', methods=['POST'])
def arraySearchBinary():
    '''Takes sequence and value, searches value in sequence with binary 
    search alghoritm'''
    json_data = request.get_json()
    if json_data is None:
        return "Empty data from client"
    else:
        print("Got data from client", json_data)

    work_data = json.loads(json_data)
    t_arr = []
    for key, value in work_data.items():
        t_arr.append(value)
    
    # start searching and result operating
    search_result = b_search(t_arr[0], t_arr[1])

    if search_result == False:
        return "wrong query data, please, recheck request"
    else:
        answer = {'search_element_index':search_result}
        send_request_info(work_data, answer)
        return answer

# === test route, remove before prod
@app.route('/home_tree')
def home_tree():
    return('home tree')

def b_search(seq, value):
    print('Got sequence:',seq,' value to find:',value)

    # validation and preparation
    try:
        seq.sort()
    except:
        return False
    finally:
        if isinstance(value, int) == False:
            return False
    
    list = 0
    list_length = len(seq) - 1

    while list_length >= list:
        middle = list + (list_length - list) // 2

        if seq[middle] < value:
            list = middle + 1
        elif seq[middle] > value:
            list_length = middle - 1
        else:
            return middle
    return -1

def send_request_info(s_data, result):
    connection = pika.BlockingConnection(
                pika.ConnectionParameters('127.0.0.1'))
    channel = connection.channel()

    # queue for search results
    channel.queue_declare(queue='search')

    search_data = copy.deepcopy(s_data)
    search_data.update(result)
    search_data = json.dumps(search_data)

    channel.basic_publish(exchange='', routing_key='search', body=search_data)
    request_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    print(" [x] ", request_time, "sent data for requests logging:",search_data)

    connection.close()

# app.run(port=5050)

if __name__ == '__main__':
    app.run()