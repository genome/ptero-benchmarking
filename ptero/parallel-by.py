#!/usr/bin/env python

import argparse
import copy
import itertools
import json
import requests
import time


PROTOTYPE_WORKFLOWS = {
    'echo': {
        "nodes": {
            "A": {
                "methods": [
                    {
                        "name": "execute",
                        "command_line": ["cat"],
                    }
                ],
                "parallelBy": "parallel_param"
            }
        },

        "edges": [
            {
                "source": "input connector",
                "destination": "A",
                "sourceProperty": "in_parallel",
                "destinationProperty": "parallel_param"
            },
            {
                "source": "A",
                "destination": "output connector",
                "sourceProperty": "parallel_param",
                "destinationProperty": "out_parallel"
            }
        ],

        "inputs": {},
        "environment": {}
    },

    'sleep': {
        "nodes": {
            "A": {
                "methods": [
                    {
                        "name": "execute",
                        "command_line": ["/usr/local/bin/benchmark_sleep"]
                    }
                ],
                "parallelBy": "sleeptime"
            }
        },

        "edges": [
            {
                "source": "input connector",
                "destination": "A",
                "sourceProperty": "in_parallel",
                "destinationProperty": "sleeptime"
            },
            {
                "source": "A",
                "destination": "output connector",
                "sourceProperty": "sleeptime",
                "destinationProperty": "out_parallel"
            }
        ],

        "inputs": {},
        "environment": {}
    }
}


def echo_inputs(size):
    return ['kitten-' + str(i) for i in xrange(size)]


def sleep_inputs(size):
    return list(itertools.repeat(0.1, size))


INPUTS_MAP = {
    'echo': echo_inputs,
    'sleep': sleep_inputs,
}



def main():
    args = parse_args()

    for size in args.sizes:
        serialized_workflow = _construct_request_body(size, type=args.type)

        start = time.time()
        wait_url = submit(args.url, serialized_workflow)
        wait(wait_url, size, args.polling_interval)
        stop = time.time()

        print "%s\t%s" % (size, stop-start)


def _construct_request_body(size, type):
    workflow = copy.copy(PROTOTYPE_WORKFLOWS[type])
    workflow['inputs']['in_parallel'] = INPUTS_MAP[type](size)

    return json.dumps(workflow)


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('type', choices=['echo', 'sleep'])
    parser.add_argument('sizes', nargs='+', type=int)
    parser.add_argument('--url',
            default='http://192.168.10.10:4000/v1/workflows')
    parser.add_argument('--polling-interval', type=float, default=0.5)

    return parser.parse_args()


def submit(submit_url, data):
    response = requests.post(submit_url, data,
            headers={'Content-Type': 'application/json'})
    return _wait_url(response.headers['Location'])


def _wait_url(location_url):
    return 'http://192.168.10.10:4000/v1/reports/workflow-outputs?workflow_id=%s' % location_url.split('/')[-1]


def wait(url, expected_size, polling_interval):
    response = requests.get(url)
    while not _len_ok(response, 'out_parallel', expected_size):
        time.sleep(polling_interval)
        response = requests.get(url)

def _len_ok(response, name, expected_size):
    try:
        outputs = response.json()['outputs']
        obj = outputs.get(name)
    except Exception as e:
        print e
        print response.text
        return True

    if obj:
        return len(obj) == expected_size
    else:
        return False


if __name__ == '__main__':
    main()
