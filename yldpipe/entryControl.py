#!/usr/bin/python3

from config_loader import ConfigLoader
from common import *

# entry manager, 
# entry control, a logical ordered list of all needed account entries in kp
class EntryControl(ConfigLoader):
    def __init__(self): #, entry=None):
        #self.entry = entry
        self.config_dir = str(data_master)
        self.cfg_age = self.load_config('vals_a-g-e.yml')
        self.cfg_entries = self.load_config('kp_wanted_entries.yml')
        # rules dep on directory

    def clean(self):
        pass
    
    def all_pattern_for_group(self):
        group = 'Weblogic'
        # sub prod
        cfg = self.cfg_entries[group]
        age = self.cfg_age
        print(cfg['loop'])
        loop = cfg['loop']
        inner = loop.pop()
        outer = loop.pop()
        print(outer, inner)
        wanted = []
        for out in age[outer]:
            for inn in age[inner]:
                adds = ['{} Domain {} {} '.format(out,inn,i) for i in cfg['items']]
                print(adds)
        print(wanted)


if __name__ == '__main__':
    ec = EntryControl()
    group = ''
    ec.all_pattern_for_group()

