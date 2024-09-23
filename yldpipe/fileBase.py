
import logging
from utils import setup_logger
from config_loader import ConfigLoader
# from base import Base
logfn = __name__+'.log'
logger = setup_logger(__name__, logfn, level=logging.DEBUG)
fn_file = {}


class FileBase(ConfigLoader):

    def init(self):
        pass
        # self.cfg_fnames = self.load_config('config_fnames.yml')

    def load_fieldnames(self):
        """ load fieldnames from config file """
        self.cfg_fnames = self.load_config('config_fnames.yml')
        return self.cfg_fnames