# instance/gunicorn.conf.py
import os
WORKERS_DICT = {
    # https://cloud.google.com/appengine/docs/standard/python3/runtime#entrypoint_best_practices
    "F1": 1,
    "F2": 2,
    "F4": 4,
    "F4_1G": 8,
    "B1": 1,
    "B2": 2,
    "B4": 4,
    "B4_1G": 8,
    "B8": 8
}

port = os.environ.get("PORT", 8080)
if os.environ.get("GAE_ENV") == "standard":
    instance_class = os.environ.get("INSTANCE_CLASS", "F1")
    workers = WORKERS_DICT[instance_class]
else:  # flexible environment
    import multiprocessing
    workers = multiprocessing.cpu_count() * 2 + 1
