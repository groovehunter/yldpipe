
import os
import glob
import yaml
from utils import setup_logger
import logging
logger = setup_logger(__name__, __name__+'.log', level=logging.DEBUG)
from common import data_master


class YamlConfigSupport:
    """ supports loading yaml config files, and setting them as class members
        loading complete deirectories of yaml files,
        and laoding several cfg layers, for example for inheritance"""
    config_dir = ''
    config_dir_master = ''

    def init_config_profile(self):
        # loads main config for profile support

        self.config_dir = str(data_master)
        fn = 'config_dp.yml'
        self.cfg_dp = self.load_config(fn)
        cfg_default = self.cfg_dp['default_profile']

        #profile = self.cfg_dp['profile']
        # use profile name given from app config
        profile = self.profile_name
        if profile is None:
            self.cfg_profile = cfg_default
        else:
            self.cfg_profile = self.cfg_dp[profile]
            # for missing keys in specific profile, use the default value
            for key in cfg_default.keys():
                if key not in self.cfg_profile:
                    self.cfg_profile[key] = cfg_default[key]

    def set_configs_as_members(self, cfg_names_list=[]):
        for name in cfg_names_list:
            fn = name + '.yml'
            logger.debug('loading config %s, set as %s', fn, 'cfg_'+name)
            setattr(self, 'cfg_'+name, self.load_config(fn))
            # logger.debug('cfg_%s: %s', name, getattr(self, 'cfg_'+name))

    def load_config(self, filename):
        path = os.path.join(self.config_dir, filename)
        with open(os.path.join(self.config_dir, filename)) as f:
            # logger.debug('loading config file %s ', f.name)
            config = yaml.safe_load(f)
        return config

    def load_config_master(self, filename):
        """ load config from master directory"""
        path = os.path.join(self.config_dir_master, filename)
        logger.debug('loading config from %s', path)
        with open(path) as f:
            logger.debug('loading config file %s from dir %s', f.name, self.config_dir)
            config = yaml.safe_load(f)
            logger.debug('DONE')
        return config

    def load_config_from_dirs(self, directories):
        """ solution for inheritance in the yaml dict """
        config = {}
        for directory in directories:
            yaml_files = glob.glob(os.path.join(directory, "*.yaml"))
            for yaml_file in yaml_files:
                with open(yaml_file, 'r') as f:
                    config.update(yaml.safe_load(f))
        return config


