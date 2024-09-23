# from config_loader import ConfigLoader
from YamlConfigSupport import YamlConfigSupport
from common import data_master
from utils import setup_logger
import logging
logger = setup_logger(__name__, __name__+'.log', level=logging.DEBUG)

from excelReader import ExcelReader
from excelWriter import ExcelWriter
from csvReader import CsvReader
from csvWriter import CsvWriter
from yamlReader import YamlReader, YamlStorage
from yamlWriter import YamlWriter
from jsonReader import JsonReader, JsonStorage
from jsonWriter import JsonWriter

class DataBroker(YamlConfigSupport):

    def class_factory(self, class_name, rw):
        if rw == 'r':
            class_name = class_name+'Reader'
        elif rw == 'w':
            class_name = class_name+'Writer'
        elif rw == 's':
            class_name = class_name+'Storage'
        # define mapping in config XXX
        classes = {
            'excelReader': ExcelReader,
            'csvReader': CsvReader,
            'excelWriter': ExcelWriter,
            'csvWriter': CsvWriter,
            #'ansibleWriter': AnsibleWriter,
            'yamlReader': YamlReader,
            'yamlWriter': YamlWriter,
            'yamlStorage': YamlStorage,
            'jsonReader': JsonReader,
            'jsonWriter': JsonWriter,
            'jsonStorage': JsonStorage,
        }
        return classes[class_name]()

    # XXX combine both, usage check!
    # XXX add klass_cfg as param ? And use default from config as fallback
    def init_reader_class(self):
        klass_cfg = self.cfg_profile['reader']
        return self.class_factory(klass_cfg, 'r')

    def init_writer_class(self):
        klass_cfg = self.cfg_profile['writer']
        return self.class_factory(klass_cfg, 'w')

    def init_storage_src_class(self):
        klass_cfg = self.cfg_profile['storage_src']
        return self.class_factory(klass_cfg, 's')

    def init_storage_dst_class(self):
        klass_cfg = self.cfg_profile['storage_dst']
        return self.class_factory(klass_cfg, 's')



class ExcelCache(DataBroker):
    """ class for caching """

    def __init__(self):
        pass


    def init_cache(self):
        logger.debug('self.cfg_profile: %s', self.cfg_profile)
        self.init_reader_class()
        self.reader.setatt(cfg_si=self.cfg_si,
                           sub=self.cfg_profile['sub_in'])
        self.reader.init_reader()

