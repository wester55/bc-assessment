import json
import multiprocessing
import requests
from time import sleep
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def alert(details):
    print("Here we send alert to someone somehow, details {}".format(details))


def simple_get(url, timeout, pid):
    print()
    print("PID {} testing {} with timeout {}".format(pid, url, timeout))
    try:
        resp = requests.get(url, verify=False, timeout=timeout)
        resp.raise_for_status()
    except requests.exceptions.RequestException as err:
        alert(err)


def run_check(test_details):
    # we need some high default latency so our process will not get stuck
    default_max_latency = 10
    our_pid = multiprocessing.current_process()
    if 'max_latency' in test_details:
        timeout = test_details['max_latency']
    else:
        timeout = default_max_latency
    while True:
        simple_get(test_details['url'], timeout, our_pid)
        sleep(test_details['frequency'])


if __name__ == "__main__":
    with open('monitor_config.json') as f:
        data = json.load(f)

    tests = list()
    for test_type in data.keys():
        for t in data[test_type]:
            test = dict()
            test['type'] = test_type
            for key in t.keys():
                test[key] = t[key]
            tests.append(test)

    queue = multiprocessing.Queue()
    print("Starting {} processes".format(len(tests)))
    processes = [multiprocessing.Process(target=run_check, args=(test,)) for test in tests]

    for p in processes:
        p.start()

    for p in processes:
        p.join()
