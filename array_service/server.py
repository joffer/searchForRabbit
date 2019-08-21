import copy
from datetime import datetime
import json
import logging

from flask import Flask, request, Response
import pika

app = Flask(__name__)

# initialize logging
log_path = 'logs/search_log.log'
log_format = '%(asctime)s - %(message)s'
current_logger = '__name__'

logger = logging.getLogger(current_logger)
log_file = logging.FileHandler(log_path)
logger.setLevel(logging.INFO)
formatter = logging.Formatter(log_format)
log_file.setFormatter(formatter)
logger.addHandler(log_file)

# rabbit queue connection 
connection_address = '127.0.0.1'
active_queue = 'search'
connection = pika.BlockingConnection(
                pika.ConnectionParameters(connection_address))
channel = connection.channel()
channel.queue_declare(queue=active_queue)

@app.route('/array/search/binary/', methods=['POST'])
def array_search_binary():
    '''Takes sequence and int value, searches value in sequence with binary 
    search alghoritm'''
    # validation incoming data
    json_data = request.get_json()

    if not json_data:
        return compile_error({'error_message':'No data provided'})
    
    try:
        work_data = json.loads(json_data)
    except Exception:
        return compile_error({'error_message':'Invalid entry data'})

    key_list = ['search_array', 'search_element']
    if not all(key in work_data for key in key_list) or len(work_data) != 2:
        return compile_error({'error_message':'Incorrect data fields'})

    if not all(isinstance(value, int) for value in work_data['search_array']):
        return compile_error(
                {"error_message":"Invalid data in 'search_array' field"})

    if not isinstance(work_data['search_element'], int):
        return compile_error(
                {"error_message":"Invalid data in 'search_element' field"})

    temp_array = list(work_data.values())

    # start searching and result operating
    if validate_list(temp_array[0]):
        search_result = b_search(temp_array[0], temp_array[1])
    else:
        return compile_error({"error_message":"Unsorted list"})
    
    answer = {'search_element_index': search_result}
    send_request_info(work_data, answer)
    logger.info('Client data: %s, search result: %s' % 
                (work_data, search_result))
    return Response(json.dumps(answer))

def compile_error(error_text):
    '''creating error message for response'''
    response = app.response_class(
        response = json.dumps(error_text),
        status = 400,
        mimetype = 'application/json'
    )
    return response

def validate_list(temp_list):
    '''validation of incoming list for ascending'''
    for i in range(len(temp_list)-1):
        if temp_list[i] > temp_list[i+1]:
            return False
    return True

def b_search(seq, value):
    '''binary search in sorted list'''
    start_index = 0
    end_index = len(seq) - 1

    while end_index >= start_index:
        middle = start_index + (end_index - start_index) // 2

        if seq[middle] < value:
            start_index = middle + 1
        elif seq[middle] > value:
            end_index = middle - 1
        else:
            return middle
    return -1

def send_request_info(s_data, result):
    '''sending notification to rabbit queue'''
    search_data = copy.deepcopy(s_data)
    search_data.update(result)
    search_data = json.dumps(search_data)

    channel.basic_publish(exchange='', routing_key='search', body=search_data)
    logger.info("Request and result send to queue 'Search'")