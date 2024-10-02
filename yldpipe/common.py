import os
from pathlib import Path
import platform

is_windows = False

uname_info = platform.uname()
#print(uname_info)
if uname_info.system == 'Windows':
    is_windows = True
    home_dir = Path('C:/')
    project_dir = home_dir.joinpath('dev/infra_tools')
    data_in = home_dir.joinpath('dev/infra_data/data_in/')
    data_out = home_dir.joinpath('dev/infra_data/data_out/')
    data_master = home_dir.joinpath('dev/infra_tools/data_master/')
elif uname_info.system == 'Linux':
    if uname_info.node == 'flowpad':
        project_dir = Path(__file__).parent.parent
        data_dir = project_dir.parent.joinpath('yldpipe_data')
        data_in = data_dir.joinpath('data_in')
        data_out = data_dir.joinpath('data_out')
        data_master = project_dir.joinpath('data_master')

# print('project_dir: ', project_dir)
# for import_server_infra_csv.py
# and  excel_pd.py

# XXX define erow in app
# erow = ['']*5
leaf_list = []
result = []


# def examine(data, writer):
# descends tree and outputs all leaves as rows with id to print as csv
def recurse_dict_write_csv(data, writer):
    erow = [''] * 5
    for k in data.keys():
        d = data[k]
        if isinstance(d, dict):
            examine(d, writer)
        else:
            leaf_list.append(d)
            # print(d)
            row = [d]
            row = row + erow.copy()
            # print(row)
            writer.writerow(row)


examine = recurse_dict_write_csv


# descends tree and appends all leaves as rows with id to flat list
def recurse_dict_create_csv(data, erow, path):
    global result
    # global erow
    for k in data.keys():
        d = data[k]
        if isinstance(d, dict):
            path.append(k)
            recurse_dict_create_csv(d, erow, path)
            path.pop()
        else:
            path.append(k)
            print("path: ", str(path))
            leaf_list.append(d)
            path.pop()
            # print(d)
            row = [d]
            row = row + erow.copy()
            result.append(row)
