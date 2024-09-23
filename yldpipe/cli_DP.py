#!/usr/bin/python3

# from common import data_in, data_out, data_master
# from dataPipeline import DataPipeline
from dataLooper import DataLooper


# dp = DataPipeline()
dp = DataLooper()
dp.init()
dp.work_meta()


