from bioblend import galaxy
import argparse
import generate
import sys
import time


def main():
    args = parse_args()

    galaxy_client = get_galaxy_client(args)
    for size in args.size:
        workflow_data = generate.workflow(size)
        workflow = galaxy_client.workflows.import_workflow_json(workflow_data)
        history_name = 'parallel-%s' % size

        submit_workflow(galaxy_client, workflow, history_name)
        wait_for_history(galaxy_client, history_name,
                polling_time=args.polling_time)

        runtime = get_runtime(galaxy_client, history_name,
                polling_time=args.polling_time)
        print '%s\t%s' % (size, runtime)


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--url', default='http://192.168.100.100')
    parser.add_argument('--polling-time', type=float, default=0.5)


    umg = parser.add_mutually_exclusive_group(required=True)
    umg.add_argument('--create-user', action='store_true', default=False)

    parser.add_argument('--master-api-key', default='master-api-key')
    parser.add_argument('--user', default='vagrant')

    umg.add_argument('--api-key')


    parser.add_argument('size', type=int, nargs='+')

    return parser.parse_args()


def get_galaxy_client(args):
    if args.create_user:
        master_client = galaxy.GalaxyInstance(args.url, key=args.master_api_key)
        user_info = master_client.users.create_local_user(args.user,
                '%s@localhost.localdomain' % args.user, args.user)
        api_key = master_client.users.create_user_apikey(user_info.get('id'))
        sys.stderr.write('Created user %s with api key %s\n'
                % (args.user, api_key))

    else:
        api_key = args.api_key

    return galaxy.GalaxyInstance(args.url, key=api_key)


def submit_workflow(galaxy_client, workflow, history_name):
    try:
        galaxy_client.workflows.run_workflow(workflow['id'],
                history_name=history_name)
    except galaxy.client.ConnectionError:
        pass


def wait_for_history(galaxy_client, history_name, polling_time=0.5):
    history_id = get_history_id(galaxy_client, history_name)
    while not history_finished(galaxy_client, history_id):
        time.sleep(polling_time)


def get_history_id(galaxy_client, history_name, retry_time=0.5):
    history_id = None
    while history_id is None:
        try:
            histories = galaxy_client.histories.get_histories(name=history_name)
            history_id = histories[-1]['id']
        except galaxy.client.ConnectionError:
            time.sleep(retry_time)
    return history_id


_WAIT_STATES = {'queued', 'running'}
def history_finished(galaxy_client, history_id):
    try:
        return galaxy_client.histories.get_status(history_id).get('state'
                ) not in _WAIT_STATES
    except galaxy.client.ConnectionError:
        return False


def get_runtime(galaxy_client, history_name, polling_time=0.5):
    dataset_id = get_dataset_id(galaxy_client, history_name, polling_time)
    return float(galaxy_client.datasets.download_dataset(
        dataset_id).rstrip('\n'))


def get_dataset_id(galaxy_client, history_name, retry_time=0.5):
    history_id = get_history_id(galaxy_client, history_name)

    dataset_id = None
    while dataset_id is None:
        try:
            # XXX Can give the wrong ds id
            result = galaxy_client.histories.show_history(history_id)
            if len(result['state_ids']['running']) != 0:
                continue
            dataset_id = result['state_ids']['ok'][-1]
        except galaxy.client.ConnectionError:
            time.sleep(retry_time)

    return dataset_id


if __name__ == '__main__':
    main()
