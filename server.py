import copy
from datetime import datetime
import json
import logging

from flask import Flask,request
import pika

app = Flask(__name__)

# initialize logging
log_file = logging.FileHandler('Search_log.log')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(message)s')
log_file.setFormatter(formatter)
logger.addHandler(log_file)

@app.route('/array/search/binary/', methods=['POST'])
def array_search_binary():
    '''Takes sequence and value, searches value in sequence with binary 
    search alghoritm'''

    json_data = request.get_json()
    if json_data is None:
        logger.info('Empty request from client')
        return "Empty data from client"
    else:
        logger.info("Received request for search from client")

    work_data = json.loads(json_data)
    temp_array = list(work_data.values())

    # start searching and result operating
    search_result = b_search(temp_array[0], temp_array[1])

    if search_result == False:
        logger.info('Data was not acceptable, couldn\'t perform search')
        return "Wrong query data, please, recheck request"
    else:
        answer = {'search_element_index':search_result}
        logger.info('Client data: %s, search result: %s' % 
                    (work_data, search_result))
        send_request_info(work_data, answer)
        return answer

def b_search(seq, value):
    # validation and preparation
    try:
        seq.sort()
    except:
        return False
    finally:
        if not isinstance(value, int):
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
    logger.info("Request and result send to queue 'Search'")

    connection.close()

# app.run(port=5050)

if __name__ == '__main__':
    app.run()