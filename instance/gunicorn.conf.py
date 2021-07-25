import multiprocessing

workers = multiprocessing.cpu_count() * 2 + 1
forwarded_allow_ips = "*"
accesslog = "-"
errorlog = "-"
bind = "0.0.0.0:5000"
wsgi_app = "app:app"
