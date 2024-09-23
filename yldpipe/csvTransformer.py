#!/usr/bin/python3
import csv
#re, ipaddress
from pprint import pprint
from common import *
from si_cfg import out_fns
from utils import setup_logger
from transformFunc import TransformFunc
from fileBase import FileBase
from config_loader import ConfigLoader

logfn = '../log/'+__name__+'.log'
from logging import CRITICAL, DEBUG, INFO
logger = setup_logger(__name__, logfn, level=DEBUG)

#fn = data_in.joinpath('keepass/old_entries.csv')
fn = data_in.joinpath('SI/Server_Infrastruktur_FG.csv')

fn_cfg = 'config_meta.yml'

DELIM_IN = ','
pkey = 'Servername'
#pkey = 'path'
fields_get_enums = []




class CsvTransformer(TransformFunc, FileBase, ConfigLoader):
  def __init__(self):
    self.config_dir = str(data_master)
    self.sub = 'SI/'
    #self.fnames = {}
    self.count_skipped = 0
    self.count_replaced = 0
    self.fnames = {}
    self.fnames_in = {}
    self.fnames_out = {}
    self.fn_out_f = {}
    self.unique_list = {}
    self.meta = self.load_config(fn_cfg)

  def work(self):
    """ the complete work on a csv transformation in a row """
    logger.info("=== START work ")
    self.prep_out()
    self.load_fieldnames()
    self.prep_reader()
    self.prep_writer()
    self.looprows()

  def work1to1(self):
    self.prep_out()
    # useless here, just for fnames var
    self.load_fieldnames()
    self.prep_readers_fieldnames()
    #self.prep_writer()
    #self.loop_items()


  def prep_out(self):
    """ load dest fieldnames from cfg files """
    logger.info("load dest fieldnames from cfg files ")
    self.fn_out = {}
    c = 0
    for out_fn in out_fns:
      self.fn_out[c] = data_out.joinpath(self.sub + out_fn)
  
      #self.fn_out[c] = data_out.joinpath('SI/csv_pd/'+out_fn)
      c += 1

  def prep_reader(self):
    meta = self.meta
    """ open source csv and load fieldnames
        and do once if unique vals need to be collected """
    with open(fn, encoding='utf-8-sig', newline='') as csvfile:
      self.reader = csv.DictReader(csvfile, delimiter=DELIM_IN)
      self.fieldnames = self.reader.fieldnames
      # collect
      logger.debug('from source csv get fieldnames: %s ', self.fieldnames)
      for f in self.fieldnames:
        if meta.get(f):
          cmd = list(meta[f].keys())[0]
          if cmd == 'collect':
            fields_get_enums.append(f)
      for f in fields_get_enums:
        self.unique_list[f] = []


  def prep_writer(self):
    """ prepare dict of csv writers for all dest files """
    self.writer =  {}
    c = 0
    for out_fn in out_fns:
      self.fn_out_f[c] = open(self.fn_out[c], 'w') 
      self.writer[c] = csv.DictWriter(self.fn_out_f[c], fieldnames=self.fnames[c], delimiter=',')
      self.writer[c].writeheader()
      c += 1

  def loop_items(self):
    """ loop all entities needed processing: ie each csv file to its own dest file """
    c = 0
    #for item in self.items:
    for fn in out_fns:
      self.fnames_out_cur = self.fnames_out[c]
      self.fn_in = data_in.joinpath(self.sub+fn)
      self.fn_out = data_out.joinpath(self.sub+fn)
      logger.info("processing file %s", fn)
      self.fn_out_f = open(self.fn_out, 'w') 
      self.writer = csv.DictWriter(self.fn_out_f, fieldnames=self.fnames_out_cur, delimiter=',')
      self.writer.writeheader()
      # work 
      self.loop_rows()
      # work done
      self.fn_out_f.close()
      logger.info("Wrote %s to disk", self.fn_out_f)
      c += 1


  def looprows(self):
    """ open source file again and loop through all entries and call the 
        submethods to check and transform vals according to meta[f] config """
    meta = self.meta
    with open(fn, encoding='utf-8-sig', newline='') as csvfile:
      self.reader = csv.DictReader(csvfile, delimiter=DELIM_IN)
      self.rcount = 0
      for row in self.reader:
        logger.debug(row)
        # special treatment for empty rows or header rows
        if not row[pkey] or row[pkey].startswith('#'):
          logger.info("Empty or comment row, copy as is; pkey val is %s", row[pkey])
          self.count_skipped += 1
          cc = 0
          for out_fn in out_fns:
            fresh = {}
            fresh[pkey] = "# ---"
            for f in self.fnames[cc]:
              fresh[f] = ""
            self.writer[cc].writerow(fresh)
            cc += 1
          continue

        # content rows
        logger.debug(row)
        cc = 0
        for out_fn in out_fns:
          fresh = {}
          for f in self.fnames[cc]:
            if f not in self.fieldnames:
              logger.debug("field not in source file: %s", f)
              continue
            row[f] = row[f].strip()
            fresh[f] = row[f]       # if nothing is todo, copy value
            # if none: True is set, value is allowed to be empty
            if meta[f]:
              none = meta[f].get('none')
              if none == True:
                if row[f] == '':
                  logger.debug('cell was legit empty: %s - leave ', f)
                  continue
              if row[f] != '-':
                fresh[f] = self.gener(row[f], meta[f], f)
          logger.debug("FRESH row: %s", fresh)
          self.writer[cc].writerow(fresh)
          cc += 1
        self.rcount += 1

  def report(self):
    print("------------------ REPORT ")
    print("count_skipped: ", self.count_skipped)
    print("count_replaced: ", self.count_replaced)
    print("row count: ", self.rcount)
    c = 0
    for out_fn in out_fns:
      logger.debug("=== fnames[%s]", str(c))
      logger.debug(self.fnames[c])
      c += 1


  ### list all possible values to collect 
  def all_values(self):
    for f in self.fields_get_enums:
      self.unique_list[f].sort()
      #print(f)
      #print("\n".join(unique_list[f]))
      #print("------------------------")

