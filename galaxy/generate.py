import argparse
import copy
import json
import uuid


STEP = json.loads(r'''
{
    "annotation": "",
    "input_connections": {
        "start_time_file": {
            "id": 0,
            "output_name": "start_time_file"
        }
    },
    "inputs": [],
    "name": "Sleep",
    "outputs": [
        {
            "name": "result",
            "type": "tabular"
        }
    ],
    "position": {
        "left": 520,
        "top": 1015
    },
    "post_job_actions": {
        "HideDatasetActionresult": {
            "action_arguments": {},
            "action_type": "HideDatasetAction",
            "output_name": "result"
        }
    },
    "tool_errors": null,
    "tool_id": "benchmark_sleep",
    "tool_state": "{\"__page__\": 0, \"__rerun_remap_job_id__\": null, \"start_time_file\": \"null\", \"sleeptime\": \"\\\"0.1\\\"\"}",
    "tool_version": "1.0.0",
    "type": "tool",
    "user_outputs": []
}
''')


START = json.loads(r'''
{
    "annotation": "",
    "id": 0,
    "input_connections": {},
    "inputs": [],
    "name": "Sleep Start",
    "outputs": [
        {
            "name": "start_time_file",
            "type": "tabular"
        }
    ],
    "position": {
        "left": 200,
        "top": 200
    },
    "post_job_actions": {
        "HideDatasetActionstart_time_file": {
            "action_arguments": {},
            "action_type": "HideDatasetAction",
            "output_name": "start_time_file"
        }
    },
    "tool_errors": null,
    "tool_id": "benchmark_sleep_start",
    "tool_state": "{\"__page__\": 0, \"__rerun_remap_job_id__\": null}",
    "tool_version": "1.0.0",
    "type": "tool",
    "user_outputs": []
}
''')

STOP = json.loads(r'''
{
    "annotation": "",
    "input_connections": {
        "start_time_file": {
            "id": 0,
            "output_name": "start_time_file"
        }
    },
    "inputs": [],
    "name": "Sleep Stop",
    "outputs": [
        {
            "name": "run_time_file",
            "type": "tabular"
        }
    ],
    "position": {
        "left": 852,
        "top": 201
    },
    "post_job_actions": {},
    "tool_errors": null,
    "tool_id": "benchmark_sleep_stop",
    "tool_state": "{\"__page__\": 0, \"__rerun_remap_job_id__\": null, \"sleep_result\": \"null\", \"sleepresults\": \"[{\\\"__index__\\\": 0, \\\"sleep_result\\\": null}, {\\\"__index__\\\": 1, \\\"sleep_result\\\": null}, {\\\"__index__\\\": 2, \\\"sleep_result\\\": null}, {\\\"__index__\\\": 3, \\\"sleep_result\\\": null}, {\\\"__index__\\\": 4, \\\"sleep_result\\\": null}, {\\\"__index__\\\": 5, \\\"sleep_result\\\": null}, {\\\"__index__\\\": 6, \\\"sleep_result\\\": null}, {\\\"__index__\\\": 7, \\\"sleep_result\\\": null}, {\\\"__index__\\\": 8, \\\"sleep_result\\\": null}, {\\\"__index__\\\": 9, \\\"sleep_result\\\": null}]\", \"start_time_file\": \"null\"}",
    "tool_version": "1.0.0",
    "type": "tool",
    "user_outputs": []
}
''')


def tool_state(number):
    return json.dumps(
        {
            '__page__': 0,
            '__rerun_remap_job_id__': None,
            'sleep_result': "null",
            'sleepresults': json.dumps([{
                '__index__': i,
                'sleep_result': None,
                }
                for i in xrange(number)
            ]),
            'start_time_file': "null",
        }
    )


def workflow(number):
    return {
        "a_galaxy_workflow": "true",
        "annotation": "",
        "format-version": "0.1",
        "name": "ParallelBy-%d" % number,
        "steps": steps(number),
        "uuid": str(uuid.uuid4()),
    }


def steps(number):
    results = {}
    results['0'] = START
    for i in xrange(1, number + 1):
        results[str(i)] = sleep_step(i)
    results[str(number + 1)] = stop_step(number)
    return results


def sleep_step(index):
    s = copy.copy(STEP)
    s['id'] = index
    return s


def stop_step(number):
    s = copy.copy(STOP)
    s['id'] = number + 1
    s['tool_state'] = tool_state(number)
    s['input_connections'] = input_connections(number)

    return s



def input_connections(number):
    result = {
        "start_time_file": {
            "id": 0,
            "output_name": "start_time_file",
        }
    }

    for i in xrange(number):
        result.update(input_connection(i))
    return result


def input_connection(node_id):
    return {
        'sleepresults_%d|sleep_result' % node_id: {
            'id': node_id + 1,
            'output_name': 'result',
        }
    }


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('size', type=int)

    return parser.parse_args()


def main():
    args = parse_args()

    print json.dumps(workflow(args.size))


if __name__ == '__main__':
    main()
