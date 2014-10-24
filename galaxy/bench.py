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
        result = galaxy_client.workflows.run_workflow(workflow['id'],
                history_name='parallel-%s' % size)
        runtime = get_runtime(galaxy_client, result['outputs'][-1],
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


_WAIT_STATES = {'queued', 'running'}
def get_runtime(galaxy_client, dataset_id, polling_time=0.5):
    while galaxy_client.datasets.show_dataset(dataset_id
            ).get('state') in _WAIT_STATES:
        time.sleep(polling_time)
    return float(galaxy_client.datasets.download_dataset(
        dataset_id).rstrip('\n'))


if __name__ == '__main__':
    main()
