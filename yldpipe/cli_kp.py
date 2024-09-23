#!/usr/bin/python3

from keepassReader import treeReorderReader
from common import data_out, data_master

fn = str(data_master.joinpath('kp_tree_team.yml'))
fn_pathmap = str(data_master.joinpath('kp_pathmap.yml'))
legacy_db = '/srv/ansible_workdir/eip.kdbx'
new_db =  str(data_out.joinpath('keepass/eip_NG.kdbx'))

kpr = treeReorderReader()
#data = kpr.data
#kpr.create_new_etree_rec_from_dict(data)
kpr.prep_transfer()
kpr.rec_walk_tree(kpr.kp_src.root_group)
kpr.kp_dst.save()
kpr.report()
#kpr.rec_walk_tree(kpr.kp_dst.root_group)

