# -*-coding:utf8-*-

from configparser import ConfigParser
from scan import Scan, Config

config = ConfigParser()

with open('config') as f:
    config.read_file(f)

connect, root = config['zookeeper'].values()
scan = Scan(Config.loads(connect, root))
scan.start()
try:
    scan.join()
except KeyboardInterrupt:
    scan.stop()
