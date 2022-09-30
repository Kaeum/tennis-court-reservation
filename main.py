import multiprocessing
multiprocessing.freeze_support()

import datetime
import traceback
from joblib import Parallel, delayed
from yangjae.reservation import Reservation


def make_reservation(i):
    dt = datetime.datetime(2022, 10, 1, 9, 0, 0, 0)
    r = Reservation(i.get('court_id'), i.get('date'), i.get('start_time'), i.get('end_time'), dt)
    try:
        r.process()
    except Exception:
        traceback.print_exc()


def run_in_parallel():
    inputs = [
        {'court_id': 4344692, 'date': '2022-11-05', 'start_time': '6:00', 'end_time': '9:00'},
        {'court_id': 4344692, 'date': '2022-11-12', 'start_time': '6:00', 'end_time': '9:00'},
        {'court_id': 4344692, 'date': '2022-11-19', 'start_time': '6:00', 'end_time': '9:00'},
        {'court_id': 4344692, 'date': '2022-11-26', 'start_time': '6:00', 'end_time': '9:00'},
        {'court_id': 4344694, 'date': '2022-11-19', 'start_time': '6:00', 'end_time': '9:00'},
        {'court_id': 4344694, 'date': '2022-11-26', 'start_time': '6:00', 'end_time': '9:00'}
    ]
    Parallel(n_jobs=-1, prefer='threads')(delayed(make_reservation)(i) for i in inputs)


if __name__ == '__main__':
    run_in_parallel()
