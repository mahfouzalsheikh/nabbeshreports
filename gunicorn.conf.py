import os
import sys
import multiprocessing

def app_path():
    sys.path.append('/home/code/po/')
    sys.path.append('/home/code/po/ball/')
    return

def num_cpus():
    cpus = 0
    try:
        cpus = os.sysconf("SC_NPROCESSORS_ONLN")
    except:
        cpus =  multiprocessing.cpu_count()

    if cpus: return cpus
    else: return 3





bind = "127.0.0.1:8888"
logfile = "/var/log/gunicorn.log"

#workers   = num_cpus()*2 + 1
workers = 3
debug     = True
daemon    = True
#django_settings  = 'settings.py'
pythonpath = '/usr/bin/python'
