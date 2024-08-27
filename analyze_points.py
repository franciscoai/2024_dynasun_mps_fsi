'''
Reads /output/selected_points.csv and computes and plots some derived quantities
'''
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys

#CONSTANTS
repo_path = os.getcwd()
output_dir = repo_path + '/output/plots'
points_list = repo_path + '/output/selected_points.csv'
#####
os.makedirs(output_dir, exist_ok=True)
# reads csv ith  ['file', 'lon [arcsec]', 'lat [arcsec]']
points = pd.read_csv(points_list)
breakpoint()
