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
current_queue = 'search'
connection = pika.BlockingConnection(
                pika.ConnectionParameters(connection_address))
channel = connection.channel()
channel.queue_declare(queue=current_queue)

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
    elif not validate_list(work_data['search_array']):
        return compile_error({"error_message":"Unsorted list"})

    if not isinstance(work_data['search_element'], int):
        return compile_error(
                {"error_message":"Invalid data in 'search_element' field"})

    return Response(start_search(work_data))

def start_search(client_data):
    '''search execution and result processing'''
    search_result = b_search(client_data['search_array'], 
                                client_data['search_element'])

    answer_text = {'search_element_index': search_result}

    # sending to rabbit queue
    search_data = copy.deepcopy(client_data)
    search_data.update(answer_text)
    search_data = json.dumps(search_data)
    send_request_info(search_data, current_queue)

    logger.info('Client data: %s, search result: %s' % 
                (client_data, search_result))
    return json.dumps(answer_text)

def compile_error(error_text):
    '''creating error message for response with code 400'''
    response = app.response_class(
        response = json.dumps(error_text),
        status = 400,
        mimetype = 'application/json'
    )
    return response

def validate_list(temp_list):
    '''validation of incoming list for ascending order'''
    for i in range(len(temp_list)-1):
        if temp_list[i] > temp_list[i+1]:
            return False
    return True

def b_search(seq, value):
    '''execution of binary search - "int" value in ascending sorted list
    returns value index or "-1" if value is not present in list '''
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

def send_request_info(resulting_data, active_queue):
    '''sending result notification to rabbit queue'''
    
    channel.basic_publish(exchange='', 
                            routing_key=active_queue, body=resulting_data)
    logger.info("Request and result send to queue: " + active_queue)