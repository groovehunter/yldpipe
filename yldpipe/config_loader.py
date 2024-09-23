import os
import glob
import yaml
from utils import setup_logger
import logging
logger = setup_logger(__name__, __name__+'.log', level=logging.DEBUG)
from common import data_master


class ConfigLoader:
    config_dir = str(data_master)
    config_dir_master = str(data_master)
    # XXX remove init
    # def __init__(self, config_dir):
    #     self.config_dir = config_dir

    def load_config_from_dirs(self, directories):
        config = {}
        for directory in directories:
            yaml_files = glob.glob(os.path.join(directory, "*.yaml"))
            for yaml_file in yaml_files:
                with open(yaml_file, 'r') as f:
                    config.update(yaml.safe_load(f))
        return config

    # original method
    def load_config(self, filename):
        path = os.path.join(self.config_dir, filename)
        logger.debug('loading config from %s', path)
        with open(os.path.join(self.config_dir, filename)) as f:
            logger.debug('loading config file %s from dir %s', f.name, self.config_dir)
            config = yaml.safe_load(f)
            logger.debug('DONE')
        return config
    def load_config_master(self, filename):
        path = os.path.join(self.config_dir_master, filename)
        logger.debug('loading config from %s', path)
        with open(path) as f:
            logger.debug('loading config file %s from dir %s', f.name, self.config_dir)
            config = yaml.safe_load(f)
            logger.debug('DONE')
        return config

    def load_config_file(self, filepath):
        """ load config from a specific file path """
        with open(filepath) as f:
            config = yaml.safe_load(f)
        return config

    def setatt(self, **kwargs):
        """ set any attribute of the class by kwargs """
        for a, v in kwargs.items():
            setattr(self, a, v)

    def get_item_by_path(self, data, path):
        """ yaml dict is a nested dict, this method gets the value by path"""
        keys = path.split('.')
        item = data
        for key in keys:
            item = item[key]
        return item

    def print_data(self, data):
        """ print yaml dict """
        for key, value in data.items():
            print(f"Key: {key}, Value: {value}")

