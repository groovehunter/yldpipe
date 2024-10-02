#from dataBroker import ExcelCache

from utils import setup_logger
import logging
logger = setup_logger(__name__, __name__+'.log', level=logging.DEBUG)

class ExternalDataInterface:
    def set_reader(self, reader):
        pass
    def call_method(self, method, *args):
        return self.mapping[method](*args)


class MetadataSearch(ExternalDataInterface):
    def __init__(self):
        self.mapping = {
            'get_data_for_one': self.get_metadata_for_url,
            'get_all_of_x': self.get_all_topics
        }

    def get_metadata_for_url(self, url):
        return {}

    def get_all_topics(self, domain):
        # lookup all entries of column <domain> in metadata
        return []


# XXX XXX BIG!
# refactor this to subclass from ExcelReader
class SICache(ExternalDataInterface):  #(ExcelCache):
    def __init__(self):
        self.mapping = {
            'get_data_for_one': self.get_hosts_for_app,
            'get_all_of_x': self.get_hosts_all,
            'get_attr_all_of_x': self.get_all_hosts_attr,
        }
        self.si_data = None

    def set_reader(self, reader):
        self.reader = reader

    def cache_si_data(self):
        # XXX cleanup methdods and members

        self.reader.setatt(cfg_si=self.cfg_si)
        self.reader.set_src_dir(self.cfg_si['data_in'].joinpath('SI'))
        self.reader.init_reader()

        logger.debug('self.cfg_si: %s', self.cfg_si)
        if len(self.reader.buffer) == 0:
            self.reader.read_first()
        self.si_data = self.reader.get_buffer(self.cfg_si['in_fns'][0])


    # XXX new class sth like "ServerDataInterface" ?
    # XXX cache for all roles in a dict
    def get_hosts_for_app(self, role):
        # logger.debug('role: %s', role)
        if self.si_data is None:
            self.cache_si_data()
        data = self.si_data.fillna('')
        result = data[data['Rolle']==role]
        return result['Servername'].tolist()
    def get_hosts_all(self):
        if self.si_data is None:
            self.cache_si_data()
        data = self.si_data.fillna('')
        result = data[data['Rolle'].str.startswith('e')]
        return result['Servername'].tolist()

    def get_all_hosts_attr(self, attr):
        if self.si_data is None:
            self.cache_si_data()
        data = self.si_data.fillna('')
        data = data[data['Rolle'].str.startswith('e')]
        result = data[attr].tolist()
        return result

    def get_data_for_host(self, hostname):
        if self.si_data is None:
            self.cache_si_data()
        data = self.si_data.fillna('')
        result = data[data['Servername']=='zrz-ux-'+hostname]
        logger.debug('for host %s result len is: %s', hostname, len(result))
        if len(result) == 0:
            return None
        data = result.to_dict('records')[0]
        return data

    def get_app_for_host(self, hostname):
        if self.si_data is None:
            self.cache_si_data()
        data = self.si_data.fillna('')
        result = data[data['Servername']=='zrz-ux-'+hostname]
        role = result['Rolle'].tolist()[0]
        #logger.debug('role: %s', role)
        app = role.split('_')[0]
        return app

    def get_hosts_for_group(self, group_name):
        logger.debug('group_name: %s', group_name)
        # is reader done?
        if self.si_data is None:
            self.cache_si_data()
        data = self.si_data.fillna('')
        # logger.debug(data['Rolle'][30:80])
        # logic = self.cfg_kp_wanted_logic['map_kpgroup_agekey'][group_name]
        logic = 'eIP' # XXX used only by group_do_entries_loop_age ??
        if isinstance(logic, dict):
            logic = logic['OR']
            mask = data['Rolle'].apply(lambda x: any(s in str(x) for s in logic))
        else:
            mask = data['Rolle'].str.contains(logic)
        logger.debug('logic: %s', logic)
        # logger.debug('mask: \n %s', mask[30:35])
        data = data[mask]
        # criteria = "data['Rolle'].str.contains('%s')" %(logic)
        #data = self.filter_rows_by_crit(data=buffer, criteria=criteria)
        return data

