#!/usr/bin/env python

import argparse
import copy
import itertools
import json
import requests
import time


PROTOTYPE_WORKFLOWS = {
    'echo': {
        "tasks": {
            "A": {
                "methods": [
                    {
                        "name": "execute",
                        "service": "ShellCommand",
                        "parameters": {
                            "commandLine": ["cat"],
                        },
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
        "tasks": {
            "start": {
                "methods": [
                    {
                        "name": "execute",
                        "service": "ShellCommand",
                        "parameters": {
                            "commandLine": ["/usr/local/bin/benchmark_start"]
                        },
                    }
                ],
            },
            "sleep": {
                "methods": [
                    {
                        "name": "execute",
                        "service": "ShellCommand",
                        "parameters": {
                            "commandLine": ["/usr/local/bin/benchmark_sleep"]
                        },
                    }
                ],
                "parallelBy": "sleeptime"
            },
            "stop": {
                "methods": [
                    {
                        "name": "execute",
                        "service": "ShellCommand",
                        "parameters": {
                            "commandLine": ["/usr/local/bin/benchmark_stop"]
                        },
                    }
                ]
            }
        },

        "edges": [
            {
                "source": "input connector",
                "destination": "start",
                "sourceProperty": "in_parallel",
                "destinationProperty": "unused_sleeptimes"
            },
            {
                "source": "input connector",
                "destination": "sleep",
                "sourceProperty": "in_parallel",
                "destinationProperty": "sleeptime"
            },
            {
                "source": "start",
                "destination": "sleep",
                "sourceProperty": "start_time",
                "destinationProperty": "unused_start_time"
            },
            {
                "source": "sleep",
                "destination": "stop",
                "sourceProperty": "sleeptime",
                "destinationProperty": "unused_sleeptimes"
            },
            {
                "source": "start",
                "destination": "stop",
                "sourceProperty": "start_time",
                "destinationProperty": "start_time"
            },
            {
                "source": "stop",
                "destination": "output connector",
                "sourceProperty": "run_time",
                "destinationProperty": "run_time"
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

        outputs_url = submit(args.url, serialized_workflow)
        run_time = _get_run_time(outputs_url, args.polling_interval)

        print "%s\t%s" % (size, run_time)


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
    parser.add_argument('--polling-interval', type=float, default=10)

    return parser.parse_args()


def submit(submit_url, data):
    response = requests.post(submit_url, data,
            headers={'Content-Type': 'application/json'})
    return _wait_url(response.headers['Location'])


def _wait_url(location_url):
    return 'http://192.168.10.10:4000/v1/reports/workflow-outputs?workflow_id=%s' % location_url.split('/')[-1]


def _get_run_time(url, polling_interval):
    run_time = _instantaneous_run_time(url)
    while run_time is None:
        time.sleep(polling_interval)
        run_time = _instantaneous_run_time(url)
    return run_time


def _instantaneous_run_time(url):
    response = requests.get(url)
    assert(response.status_code in [200, 500, 502])

    if response.status_code == 200:
        outputs = response.json()['outputs']
        return outputs.get('run_time')


if __name__ == '__main__':
    main()
