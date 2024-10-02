import pandas as pd
import re
import string

from utils import setup_logger
import logging
logger = setup_logger(__name__, __name__+'.log', level=logging.DEBUG)
lg = setup_logger(__name__+'_2', __name__+'_2.log')

class TreeReorderBuilderWanted:

    def allgroups_age_dump_entries(self):
        groups_new = []
        work = self.cfg_kp_logic_ctrl.get('work', [])
        # self.frame_fields['entries_old_table'] = self.cfg_kp_process_fields['entries_old_table']
        # self.frame_fields['entries_old_table'] = self.frame_fields['entries_old_sm_table']
        if 'dump_wanted' in work:
            groups_new += self.cfg_kp_logic_ctrl.get('loop_crit', [])
        if 'dump_copyall' in work:
            groups_new += self.cfg_kp_logic_ctrl.get('loop_copyall', [])
        if 'dump_hostspecific' in work:
            groups_new += self.cfg_kp_logic_ctrl.get('loop_hostspecific', [])

        if groups_new == []:
            return
        for group_name_new in groups_new:
            lg.debug('group_name_new: %s', group_name_new)
            group_name_old = self.groups_map_new_to_old(group_name_new)
            self.dump_group_entries(group_name_old, group_name_new)

    def dump_group_entries(self, group_name_old, group_name_new):
        lg.debug('Entering. group_name_old: %s, group_name_new: %s', group_name_old, group_name_new)
        group_obj_old = self.kp_src.find_groups_by_path(group_name_old)
        lg.debug('DUMPING group_obj_old: %s', group_obj_old)
        entry_attrs = self.cfg_kp_process_fields['kp_old_fields'] + self.cfg_kp_process_fields['kp_same_fields']
        entries = group_obj_old.entries
        #entries = group_obj_old.children
        # logger.debug('entries: %s', entries[:5])
        lg.debug('len entries: %s', len(entries))
        df_entries = pd.DataFrame(columns=self.frame_fields['entries_old_table'])
        self.stats_init()
        for entry in entries:
            row = {}
            row['status'] = 'UNTOUCHED'
            #logger.debug('entry title: %s', entry.title)
            if not 'check_entry_for_prominent_terms' in self.cfg_kp_logic_ctrl['step_skip']:
                row = self.check_entry_for_prominent_terms(entry, row)
            # logger.debug('row: %s', row)
            # XXX can check_entry_for_prominent_terms be after the old val assertion?
            # logger.debug('row: %s', row)
            for attr in entry_attrs:
                if attr.endswith('_old'):
                    row[attr] = getattr(entry, attr[:-4])
                else:
                    row[attr] = getattr(entry, attr)
            if 'path_old' in row:
                row['path_old'] = str(row['path_old'])

            row['pk'] = self.count
            self.count += 1
            ldf = len(df_entries)
            df_entries.loc[ldf] = row
        self.stats_report(name='10_dump_'+group_name_new)
        ## df_entries = df_entries.sort_values(by=self.cfg_kp_wanted_logic['sort'])
        self.df_d['entries_old'][group_name_old] = df_entries.fillna('')
        self.buffer_names_d['entries_old'][group_name_old] = group_name_old
        # lg.debug('self.df_entries columns: %s', self.df_d['entries_old'][group_name_old].columns)

    def check_entry_for_prominent_terms(self, entry, row):
        """ in entries there are certain terms at typical places,
            like in the title or the notes, ie. the behoerde or the criticality
        """
        # XXX make this much more specific, which fields should be searched in for a value
        # instead of search all everywhere, this is an extra option as last resort
        field_variations = self.cfg_kp_term_attr_logic['field_variations']
        field_search= self.cfg_kp_term_attr_logic['field_search']
        field_search_spec = self.cfg_kp_term_attr_logic['field_search_spec']

        age_sig = {
            'hostname': None,
            'item': None,
            'app': None,
            'crit': None,
            'behoerde': None,
        }
        logger.debug('group: %s - entry: %s', 'see log-2', entry)

        for key, item in field_search_spec.items():
            # lg.debug('item: %s', item)
            method, argu = next(iter(item['how'].items()))
            # logger.debug('method: %s, argu: %s', method, argu)
            if method == 're':
                cpat = re.compile(argu)
                val = getattr(entry, item['where'])
                if val is None:
                    val = ''
                # logger.debug('val: %s', val)
                m = cpat.findall(val)
                if m:
                    # logger.debug('val: %s, m: %s', val, m)
                    age_sig[item['finds']] = m[0]


        for attr in self.cfg_kp_process_fields['kp_pure_fields']+self.cfg_kp_process_fields['kp_same_fields']:

            text = str(getattr(entry, attr))
            logger.debug('attr: %s - text: %s', attr, text)
            if text is None or text=='':
                continue
            for fv_key, fv_item in field_variations.items():
                for aspect_key, aspect_item in fv_item.items():
                    all_vars = [aspect_key] + aspect_item
                    for term in all_vars:
                        cterm = re.compile(term)
                        # logger.debug('cterm: %s', cterm)
                        m = cterm.findall(text)
                        if m:
                            # if there was already a value from other term found before,
                            # dont replace vorProd with Prod # XXX solve reg exp in yaml issue
                            if age_sig[fv_key] is None:
                                age_sig[fv_key] = term
                            age_sig[fv_key] = aspect_key

            for fs_key, fs_item in field_search.items():
                # logger.debug('fs_key: %s, fs_item: %s', fs_key, fs_item)
                for aspect_key, aspect_item in fs_item.items():
                    m = None
                    if aspect_key == 're':
                        cpat = re.compile(aspect_item)
                        m = cpat.findall(text)
                        if m:
                            # logger.debug('text: %s, m: %s', text, m)
                            age_sig[fs_key] = m[0]
                    if aspect_key == 'enum':
                        for term in aspect_item:
                            m = re.findall(term, text)
                            if m:
                                # lg.debug('text: %s, m: %s', text, m)
                                age_sig[fs_key] = aspect_key
                                if 'mark' in field_search[fs_key].keys():
                                    # logger.debug('== mark: %s', field_search[fs_key]['mark'])
                                    row['status'] = field_search[fs_key]['mark']
                                if 'modify' in field_search[fs_key].keys():
                                    # XXX make easier and clearer
                                    val = list(field_search[fs_key]['modify'].values())[0]
                                    kk = list(field_search[fs_key]['modify'].keys())[0]
                                    # logger.debug('fs_key: %s, key: %s, val: %s', fs_key, kk, val)
                                    age_sig[list(field_search[fs_key]['modify'].keys())[0]] = val
                                    #row['sig_' + list(field_search[fs_key]['modify'].keys())[0]] = list(field_search[fs_key]['modify'].values())[0]

        logger.debug('age_sig: %s', age_sig)
        result = {}
        for key, d_item in age_sig.items():
            # what condition was here? XXX
            if True:
                result['sig_'+key] = d_item
            #if key == 'item':
            #    result['item'] = d_item
        row.update( result )
        logger.debug('row: %s', row)
        return row  #age_sig

    def allgroups_old_match(self, group_list):
        if group_list is None:
            return
        for group_name_new in group_list:
            group_name_old = self.groups_map_new_to_old(group_name_new)
            group_logic = self.cfg_kp_wanted_logic[group_name_new]
            self.group_match_sitags_oldentries(group_name_old, group_name_new, group_logic)

    # XXX rename : just allgroups_do_cases
    def allgroups_age_do_cases(self, groups_new):
        step_skip = self.cfg_kp_logic_ctrl['step_skip']
        for group_name_new in groups_new:
            lg.debug('group_name_new: %s', group_name_new)
            group_name_old = self.groups_map_new_to_old(group_name_new)
            group_obj_old = self.kp_src.find_groups_by_path(group_name_old, use_default_group=True)
            group_logic = self.cfg_kp_wanted_logic[group_name_new]
            # lg.debug('group_logic: %s', group_logic)

            if group_logic.get('case_1') is not None:
                # There are multiple cases to be handled
                for index, case_logic in group_logic.items():
                    case_name = group_name_new + '_' + str(index)
                    # XXX check if HS or AGE
                    # and call the right method for generate_wanted_table
                    self.group_generate_wanted_table(group_obj_old, group_name_new, case_name, case_logic)
                    #self.group_wanted_main_workflow(group_name_old, group_name_new, case_name, case)
                    if not 'group_match_by_serverlist_tags' in step_skip:
                        self.group_match_by_serverlist_tags(group_obj_old.name, group_name_new, case_name, case_logic)
                    if not 'calc_and_update_title_and_username' in step_skip:
                        self.calc_and_update_title_and_username(group_name_old, group_name_new, case_name, case_logic)
                    if not 'insert_into_tree' in step_skip:
                        self.add_df_to_new_tree(self.df_d['merged'][case_name])
                    self.buffer_names[case_name] = case_name
            else:
                case_name = group_name_new
                # XXX SAME HERE
                self.group_generate_wanted_table(group_obj_old, group_name_new, case_name, group_logic)
                #self.group_wanted_main_workflow(group_name_old, group_name_new, case_name, group_logic)
                lg.debug('step_skip: %s', step_skip)
                res= 'group_match_by_serverlist_tags' in step_skip
                lg.debug('res: %s', res)
                if not 'group_match_by_serverlist_tags' in step_skip:
                    self.group_match_by_serverlist_tags(group_obj_old.name, group_name_new, case_name, group_logic)
                if not 'calc_and_update_title_and_username' in step_skip:
                    self.calc_and_update_title_and_username(group_name_old, group_name_new, case_name, group_logic)
                if not 'insert_into_tree' in step_skip:
                    self.add_df_to_new_tree(self.df_d['merged'][case_name])
                self.buffer_names[case_name] = case_name

    def allgroups_hs_do_cases(self, groups_new):
        for group_name_new in groups_new:
            group_name_old = self.groups_map_new_to_old(group_name_new)
            lg.debug('group_name_old: %s - group_name_new: %s', group_name_old, group_name_new)
            group_obj_old = self.kp_src.find_groups_by_path(group_name_old)
            group_logic = self.cfg_kp_wanted_logic[group_name_new]

            if group_logic.get('case_1') is not None:
                # There are multiple cases to be handled
                for index, case_logic in group_logic.items():
                    case_name = group_name_new + '_' + str(index)
                    self.group_generate_wanted_table_hostspecific(group_obj_old, group_name_new, case_logic)
                    #self.group_wanted_main_workflow(group_name_old, group_name_new, case_name, case_logic)
                    self.group_match_by_hostname(group_name_old, group_name_new, case_name, case_logic)
                    self.add_df_to_new_tree(self.df_d['merged'][case_name])
            else:
                case_name = group_name_new
                # XXX SAME HERE
                self.group_generate_wanted_table_hostspecific(group_obj_old, group_name_new, group_logic)
                #self.group_wanted_main_workflow(group_name_old, group_name_new, case_name, group_logic)
                self.group_match_by_hostname(group_name_old, group_name_new, case_name, group_logic)
                self.add_df_to_new_tree(self.df_d['merged'][case_name])

    """
    def allgroups_hs_do(self):
        groups_new = self.cfg_kp_logic_ctrl['loop_hostspecific']
        #self.buffer_names_d['wanted_hs'] = {}
        for group_name_new in groups_new:
            #lg.debug('group_name_new: %s', group_name_new)
            group_name_old = self.groups_map_new_to_old(group_name_new)
            group_logic = self.cfg_kp_wanted_logic[group_name_new]
            group_obj_old = self.kp_src.find_groups_by_path([group_name_old])
            self.group_generate_wanted_table_hostspecific(group_obj_old, group_name_new, group_logic)

        # self.allgroups_age_do_cases(groups_new)
    """

    def group_generate_wanted_table_hostspecific(self, group_obj_old, group_name_new, group_logic):
        fieldnames = self.frame_fields['wanted_hostspecific_table']
        df = pd.DataFrame(columns=fieldnames)
        if group_logic.get('generate_wanted') == False:
            self.df_d['wanted'][case_name] = df
            return
        self.stats_init()
        items = group_logic.get('items')
        itemmap = group_logic.get('map')
        suffix = group_logic.get('suffix')
        attrs_new_pat_d = group_logic.get('attrs_new_pat_d')
        #hostname_list = self.broker.call_method('get_all_of_x', 'hostname')
        hostname_list = self.broker.call_method('get_attr_all_of_x', 'Servername')
        lvlrow = {
            'group_new': group_name_new,
            'group_path_new': [group_name_new],
            'group_old': group_obj_old.name,
            'status': 'UNTOUCHED',
        }
        for hostname in hostname_list:
            logger.debug('hostname: %s', hostname)
            for item in items:
                row = lvlrow.copy()
                row['hostname'] = hostname[7:14]
                row['vm'] = hostname[7:14]
                row['host'] = hostname
                row['item'] = item
                row['mapped'] = itemmap[item]
                row['fk'] = self.count
                #row['title_new'] = '%s %s' % (item, hostname)
                for key, anp_item in attrs_new_pat_d.items():
                    logger.debug('check-item: %s -- key: %s, anp_item: %s', item, key, anp_item)
                    if 'all_items' in attrs_new_pat_d[key].keys():
                        pattern = attrs_new_pat_d[key]['all_items']
                    else:
                        pattern = anp_item[item]
                    logger.debug('pattern: %s', pattern)
                    result_substd = string.Template(pattern).substitute(row)
                    logger.debug('result_substd: %s', result_substd)
                    row[key + '_new'] = result_substd
                    self.count += 1
                self.count_suc += 1
                ldf = len(df)
                df.loc[ldf] = row
        self.stats_report(name='30_generate_wanted_table_hs'+group_name_new)
        lg.debug('len df: %s', len(df))
        self.buffer_names_d['wanted'][group_name_new] = group_name_new
        self.df_d['wanted'][group_name_new] = df.sort_values(by='hostname')  # df.fillna('')

    def group_generate_wanted_table(self, group_obj_old, group_name_new, case_name, group_logic):
        fieldnames = self.frame_fields['wanted_table']
        df = pd.DataFrame(columns=fieldnames)
        if group_logic.get('generate_wanted') == False:
            self.df_d['wanted'][case_name] = df
            return

        items = group_logic.get('items')
        # lg.debug('items: %s', items)
        itemmap = group_logic.get('map') #get or {}
        app = group_logic.get('app')
        dst = group_logic.get('dst')
        group_path_new = [group_name_new]
        # dst is a optional destination subgroup
        age_pattern = group_logic.get('age')
        age_template = string.Template(age_pattern)
        sub_all = group_logic.get('sub_all')
        attrs_new_pat_d = group_logic.get('attrs_new_pat_d')
        lg.debug('attrs_new_pat_d: %s', attrs_new_pat_d)
        behoerde = ''
        self.stats_init()
        for crit in self.cfg_age['env']:
            lvlrow = {
                'crit': crit,
                'app': app,
                'group_new': group_name_new,
                'group_old': group_obj_old.name,
                'status': 'UNTOUCHED',
            }
            for item in items:
                row = lvlrow.copy()
                for sub in sub_all:
                    if group_logic['loop_gericht']:
                        behoerde = sub
                    # logger.debug('sub: %s', sub)
                    roledict = {'app': app, 'behoerde': behoerde, 'crit': crit}
                    role = age_template.substitute(roledict)
                    hostname_list = self.broker.call_method('get_data_for_one', {'role':role})
                    row['hostname_list'] = hostname_list
                    row['behoerde'] = sub  # XXX use behoerde here
                    row['item'] = item
                    row['mapped'] = itemmap.get(item, item)
                    row['fk'] = self.count
                    #row['title_new'] = '%s %s' % (crit, item)
                    for key, anp_item in attrs_new_pat_d.items():
                        # logger.debug('check-item: %s -- key: %s, anp_item: %s', item, key, anp_item)
                        if 'all_items' in attrs_new_pat_d[key].keys():
                            pattern = attrs_new_pat_d[key]['all_items']
                        else:
                            pattern = anp_item[item]
                        row[key+'_new'] = string.Template(pattern).substitute(row)

                    # for bmarks_eip
                    if group_logic.get('use_subgroups', None):
                        group_path_new = [group_name_new, sub]
                    else:
                        if dst:
                            group_path_new = [group_name_new, dst]

                    # logger.debug('group_path_new: %s', group_path_new)
                    row['group_path_new'] = group_path_new
                    self.count += 1
                    self.count_suc += 1
                    ldf = len(df)
                    df.loc[ldf] = row
        self.stats_report(name='30_generate_wanted_table_'+case_name)
        # df_wanted = self.df_wanted[case_name].copy()
        # Apply the function to each row and create a new column
        # XXX outcomment for debugging the other call
        df['role_index'] = df.fillna('').apply(self.calc_role_index, sig='', axis=1)
        self.df_d['wanted'][case_name] = df.sort_values(by='role_index')  # df.fillna('')
        self.buffer_names_d['wanted'][case_name] = case_name
        lg.debug('len df: %s', len(self.df_d['wanted'][case_name]))

    def calc_role_index(self, row, sig='', sig_item=''):
        # xxx use template here
        item_key = sig_item + 'item'
        # logger.debug('item_key: %s, row[item_key]: %s', item_key, row[item_key])
        req_fields = [(sig+var) for var in self.cfg_kp_process_fields['kp_si_fields']]
        #lg.debug('req_fields: %s', req_fields)
        #all_defined = self.filter_row_by_si_fields_defined(row, sig=sig, sig_item=sig_item)
        all_defined = False
        if all(((row[field] is not None) and (row[field] != '')) for field in req_fields):
            all_defined = True
        # logger.debug('all_defined: %s', all_defined)
        if all_defined == True:
            role_index = "%s_%s_%s_%s" % ( row[req_fields[0]], row[req_fields[1]], row[req_fields[2]], row[item_key])
            #logger.debug('role_index set to : %s ============', role_index)
            return role_index
        # if not all parts are defined the role_index should be empty string
        else:
            #logger.debug('role_index set to empty string, not all parts are defined')
            return ''


    # XXX another generate logic needed for looping only hosts of an app, for Alf serviceuser ie.
    def filter_row_by_si_fields_defined(self, row, sig='', sig_item=''):
        logger.debug('row: %s', row)
        ca = (row[sig+'app'] != None) & (row[sig+'app'] != '')
        cb = (row[sig+'behoerde'] != None) & (row[sig+'behoerde'] != '')
        cc = ((row[sig+'crit'] != None) & (row[sig+'crit'] != '') & (row[sig+'crit'] != 'Sandbox'))
        item_key = sig_item + 'item'
        logger.debug('item_key: %s', item_key)
        citem = (row[item_key] != None) & (row[item_key] != '')
        return (ca & cb & cc & citem)
    # XXX another generate logic needed for looping only hosts of an app, for Alf serviceuser ie.

    def filter_by_si_fields_defined(self, df):
        ca = ((df['app'] != None) & df['app'].notna())
        cb = ((df['behoerde'] != None) & df['behoerde'].notna())
        cc = ((df['crit'] != 'Sandbox') & df['crit'].notna())
        # citem = ((df['item'] != None) & df['item'].notna())
        citem = ((df['sig_item'] != None) & df['sig_item'].notna())
        return df[ca & cb & cc & citem]


    def group_match_sitags_oldentries(self, group_name_old, group_name_new, group_logic):
        lg.debug('Entering. group_name_old: %s, group_name_new: %s',
                 group_name_old, group_name_new)
        mask = self.df_d['entries_old'][group_name_old]['role_index'] != ''
        #mask = self.df_entries[group_name_old]['role_index'] != ''
        mask_ri_unset = self.df_d['entries_old'][group_name_old]['role_index'] == ''

        num_defined = len(self.df_d['entries_old'][group_name_old][mask])
        lg.debug('BEFORE ALL : num_defined: %s', num_defined)
        # XXX suddenlt this does not assign the value to the dataframe
        #self.df_entries[group_name_old]['role_index'] = self.df_entries[group_name_old].apply(
        #                            self.calc_role_index, sig_item='sig_', axis=1)
        # Iterate over each row in the DataFrame and update the role_index column
        logger.debug('----------------- call 1')
        self.stats_init()
        #for index, row in self.df_entries[group_name_old].iterrows():
        for index, row in self.df_d['entries_old'][group_name_old].iterrows():
            role_index = self.calc_role_index(row, sig_item='sig_')
            if role_index != '':
                # logger.debug('setting role_index to %s', role_index)
                self.df_d['entries_old'][group_name_old].at[index, 'role_index'] = role_index
                #self.df_entries[group_name_old].at[index, 'role_index'] = role_index
                self.count_suc += 1
            else:
                self.count_err += 1
                item_key = 'sig_item'
                # logger.debug('(app,beh,crit,itemkey): %s_%s_%s_%s', row['app'],row['behoerde'],row['crit'],row[item_key])
                #logger.debug('role_index is empty for %s', row['title_old'])
            self.count += 1
        self.stats_report(name='21_sitags_oldentries-call1_'+group_name_new)

        mask = self.df_d['entries_old'][group_name_old]['role_index'] != ''
        num_defined = len(self.df_d['entries_old'][group_name_old][mask])
        lg.debug('AFTER item sig : num_defined: %s', num_defined)

        #self.df_entries[group_name_old]['role_index'] = self.df_entries[group_name_old].apply(
        #                            self.calc_role_index, sig='sig_', sig_item='sig_', axis=1)
        dft = self.df_d['entries_old'][group_name_old][mask_ri_unset]
        logger.debug('--------------------------- call 2')
        self.stats_init()
        for index, row in dft.iterrows():
            role_index = self.calc_role_index(row, sig='sig_', sig_item='sig_')
            # logger.debug('role_index: %s at index %s', role_index, index)
            if role_index != '':
                #logger.debug('setting role_index to %s', role_index)
                self.df_d['entries_old'][group_name_old].at[index, 'role_index'] = role_index
                self.count_suc += 1
            else:
                self.count_err += 1
            self.count += 1
        self.stats_report(name='22_sitags_oldentries-call2_'+group_name_new)

        mask = self.df_d['entries_old'][group_name_old]['role_index'] != ''
        num_defined = self.df_d['entries_old'][group_name_old][mask].shape[0]
        lg.debug('AFTER ALL sig : num_defined: %s', num_defined)
        lg.debug('len dft: %s', len(dft))

    def group_match_by_hostname(self, group_name_old, group_name_new, case_name, group_logic):
        lg.debug('Entering. group_name_old: %s, group_name_new: %s, case_name: %s',
                 group_name_old, group_name_new, case_name)
        df_filtered = self.df_d['entries_old'][group_name_old].copy()
        df_wanted = self.df_d['wanted'][case_name].copy()
        df_filtered['hostname'] = df_filtered['sig_hostname']
        lg.debug('columns of df_filtered: %s', df_filtered.columns)
        #lg.debug('head of df_filtered: %s', df_filtered['hostname'].head())
        wanted_index = 'hostname'

        df_filtered[wanted_index] = df_filtered[wanted_index].astype(str)
        df_filtered.set_index(wanted_index, inplace=True)
        #df_filtered = df_filtered[self.frame_fields['entries_for_merge_sm_table']]
        df_filtered_debug = self.prep_debug_table(df_filtered)
        self.df_d['debug'][case_name] = df_filtered_debug
        self.buffer_names_d['debug'][case_name] = case_name

        """
        """
        lg.debug('columns of df_filtered: %s', df_filtered.columns)
        df_wanted.set_index(wanted_index, inplace=True)
        df_wanted.reset_index(inplace=True)
        #df_wanted = df_wanted[self.frame_fields['debug_w_table']]

        df_merged = df_filtered.merge(df_wanted, on=[wanted_index], how='inner', suffixes=('_old', '_wt'))
        lg.debug('len(df_d[merged]): %s', len(df_merged))
        self.df_d['merged'][case_name] = df_merged.fillna('')
        self.buffer_names_d['merged'][case_name] = case_name

    # XXX by_role_index rename
    def group_match_by_serverlist_tags(self, group_name_old, group_name_new, case_name, group_logic):
        """ filter all rows from df_entries where all kp_si_fields are not None and not 'Sandbox'
        and merge with df_wanted on the same fields """
        lg.debug('Entering. group_name_old: %s, group_name_new: %s, case_name: %s',
                 group_name_old, group_name_new, case_name)
        ## now continue with copies from the dataframes
        df_filtered = self.df_d['entries_old'][group_name_old].copy()
        df_wanted = self.df_d['wanted'][case_name].copy()

        role_index = 'role_index'
        # XXX just for now set to string
        df_filtered['role_index'] = df_filtered['role_index'].astype(str)
        df_filtered.set_index(role_index, inplace=True)
        df_filtered.reset_index(inplace=True)
        df_filtered = df_filtered[self.frame_fields['entries_for_merge_table']]
        df_filtered_debug = self.prep_debug_table(df_filtered)
        # lg.debug('columns of df_entries: %s', df_filtered.columns)
        self.df_d['debug'][case_name] = df_filtered_debug
        self.buffer_names_d['debug'][case_name] = case_name

        df_wanted['role_index'] = df_wanted['role_index'].astype(str)
        # lg.debug('columns of df_wanted: %s', df_wanted.columns)
        # lg.debug('len(df_wanted): %s', len(df_wanted))

        df_wanted.set_index(role_index, inplace=True)
        df_wanted.reset_index(inplace=True)
        df_wanted = df_wanted[self.frame_fields['debug_w_table']]
        # lg.debug('columns of df_filtered: %s', df_filtered.columns)
        # lg.debug('columns of df_wanted: %s', df_wanted.columns)
        df_merged = df_filtered.merge(df_wanted, on=['role_index'], how='inner', suffixes=('_old', '_wt'))
        # lg.debug('len(df_d['merged']): %s', len(df_d['merged']))
        self.df_d['merged'][case_name] = df_merged.fillna('')
        self.buffer_names_d['merged'][case_name] = case_name

        # Perform the merge operation with an outer join
        df_m_outer = df_filtered.merge(df_wanted, on=['role_index'], how='outer', suffixes=('_old', '_wt'))
        # Mark rows in df_filtered that do not have a match in df_wanted
        df_m_outer['status_info'] = df_m_outer.apply(lambda row: 'No Match' if row['role_index']=='' else 'Matched', axis=1)
        # Optionally, filter out the rows that were not matched
        df_not_matched = df_m_outer[df_m_outer['status_info'] == 'No Match']
        # lg.debug(self.df_d['merged'][case_name].head())
        #df_debug = self.prep_debug_table(df_not_matched)
        df_debug = self.prep_debug_table(df_m_outer)
        #lg.debug('columns of df_debug: %s', df_debug.columns)
        self.df_d['progress_wanted'][case_name] = df_m_outer
        self.buffer_names_d['progress_wanted'][case_name] = case_name


    def calc_and_update_title_and_username(self, group_name_old, group_name_new, case_name, group_logic):
        lg.debug('Entering. group_name_old: %s, group_name_new: %s, case_name: %s',
                 group_name_old, group_name_new, case_name)
        self.stats_init()

        df = self.df_d['merged'][case_name].copy()
        title_new_pat = group_logic.get('title_new_pat')
        username_new_pat_d = group_logic.get('username_new_pat_d')
        attrs_new_pat_d = group_logic.get('attrs_new_pat_d')

        #logger.debug('title_new_pat: %s', title_new_pat)
        df_up = pd.DataFrame(columns=self.frame_fields['entry_update_table'])
        for i, row in df.iterrows():
            uprow = {}
            row_d = row.to_dict()
            #logger.debug('row_d: %s', row_d)
            # logger.debug('row[title_new]: %s', row['title_new'])
            # assing to those cols which are defined in the template
            if row_d['crit_old'] != '':
                row_d['crit'] = row_d['crit_old']
                self.count_suc += 1
            else:
                row_d['crit'] = row_d['crit_wt']
                self.count_crit += 1
            row_d['item'] = row_d['sig_item']  # XXX assumption ?

            template_text = string.Template(title_new_pat)
            uprow['title_new'] = template_text.substitute(row_d)

            item = row_d['item']
            # logger.debug('item: %s', item)
            if username_new_pat_d.get(item) is None:
                uprow['username_new'] = ""
            else:
                template_text = string.Template(username_new_pat_d[item])
                uprow['username_new'] = template_text.substitute(row_d)

            for attrs_np_key, attrs_np_item in attrs_new_pat_d.items():
                logger.debug('attrs_np_key: %s, attrs_np_item: %s', attrs_np_key, attrs_np_item)

            # logger.debug('i: %s, uprow: %s', i, uprow)
            df_up.loc[i] = uprow
            self.count += 1


        lg.debug('len(df): %s, len(df_up): %s', len(df), len(df_up))
        df.update(df_up)
        # lg.debug('df.head(): %s', df[['title_new', 'username_new']].head())
        self.df_d['merged'][case_name].update(df)
        self.stats_report(name='40_calc_title_and_username_'+case_name)


    def allgroups_wanted_loop_sandbox(self):
        group_list = self.cfg_kp_logic_ctrl['loop_crit']
        lg.debug('group_lists: %s', group_list)
        for group_name_new in group_list:
            path_new = [group_name_new, 'Sandbox']
            group_name_old = self.groups_map_new_to_old(group_name_new)
            lg.debug('group_name_new: %s', group_name_new)
            lg.debug('columns: %s', self.df_d['entries_old'][group_name_old].columns)
            df_entries = self.df_d['entries_old'][group_name_old]
            sandbox_key = self.cfg_kp_wanted_logic.get('sandbox_key', 'crit')
            df_entries_sb = df_entries[df_entries[sandbox_key]=='Sandbox'].fillna('')
            group_dst = self.kp_dst.find_groups_by_path(path_new)
            drop_index_list = []
            self.stats_init()
            for i, row in df_entries_sb.iterrows():
                drop_index_list.append(i)
                # logger.debug(row['title_old'])
                try:
                    self.kp_dst.add_entry(group_dst, row['title_old'], row['username_old'], \
                                      row['password'], url=row['url'], notes=row['notes'])
                    self.count_suc += 1
                except:
                    self.count_err += 1
                self.count += 1
            if 'loop_sandbox_drop_from_old' in self.cfg_kp_logic_ctrl['work']:
                lg.debug('Dropping %s entries from %s', len(drop_index_list), group_name_old)
                self.df_d['entries_old'][group_name_old].drop(index=drop_index_list, inplace=True)
            self.stats_report(name='sandbox_'+group_name_new)

    def allgroups_wanted_loop_unknown(self):
        group_list = self.cfg_kp_logic_ctrl['loop_crit']
        for group_name_new in group_list:
            path_new = [group_name_new, 'unbekannt']
            group_name_old = self.groups_map_new_to_old(group_name_new)
            df_entries = self.df_d['entries_old'][group_name_old]
            df_entries_sb = df_entries[df_entries['status']=='UNKNOWN']
            group_dst = self.kp_dst.find_groups_by_path(path_new)
            drop_index_list = []
            lg.debug('len(df_entries_sb): %s', len(df_entries_sb))
            self.stats_init()
            for i, row in df_entries_sb.iterrows():
                drop_index_list.append(i)
                # logger.debug(row['title_old'])
                try:
                    self.kp_dst.add_entry(group_dst, row['title_old'], row['username_old'], \
                                      row['password'], url=row['url'], notes=row['notes'])
                    self.count_suc += 1
                except:
                    self.count_err += 1
                self.count += 1
            if 'loop_unknown_drop_from_old' in self.cfg_kp_logic_ctrl['work']:
                lg.debug('Dropping %s entries from %s', len(drop_index_list), group_name_old)
                self.df_d['entries_old'][group_name_old].drop(index=drop_index_list, inplace=True)
            self.stats_report(name='unknown_'+group_name_new)
