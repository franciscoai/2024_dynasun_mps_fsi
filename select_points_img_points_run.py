
from select_img_points import SelectImgPoints
import pandas as pd
import os
import numpy as np

#CONSTANTS
repo_path = os.getcwd() 
data_path = '/gehme/data/solo/fsi'
master_list = repo_path + '/FSI_CMEbubbles_Onlytraceable.csv'
id_of_events_to_process = [1]
odir = repo_path + '/output'
overwrite = False # if True, the output file will be overwritten if it already exists
color_scl = 3 # number of sigmas to control image color scale range
roi = None # Region of interest in arcsec [top_right_x, top_right_y, bottom_left_x, bottom_left_y]
exp_scl = 0.2 # Exponential scaling factor for the image
#######
# reads master list
output_file = odir + '/selected_points.csv'
os.makedirs(os.path.dirname(output_file), exist_ok=True)

master = pd.read_csv(master_list)
for id in id_of_events_to_process:
    # get start and end dates for the event id
    start_date = master[master['id'] == id]['start_date'].values[0]
    end_date = master[master['id'] == id]['end_date'].values[0]
    #convert dates that are in format YYYY-MM-DD HH:mm to timestamp
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    # search in data_path for files that are within the start and end dates
    # file structure in data_path is data_path/YYYY/MM/DD/solo_L2_eui-fsi304-image_YYYYMMDDTHHmmSSSSS_V01.fits*
    fits_files = []
    fits_files_dates = []
    for root, dirs, files in os.walk(data_path):
        for file in files:
            if file.endswith('.fits'):
                file_date = pd.to_datetime(file.split('_')[-2][0:15])
                fits_files_dates.append(file_date)
                if file_date >= start_date and file_date <= end_date:
                    fits_files.append(os.path.join(root, file))
    
    #sort files by date
    fits_files = [x for _,x in sorted(zip(fits_files_dates,fits_files))]

# Create an instance of the SelectImgPoints that selects points on the images and saves them to a .csv file
select_img_points = SelectImgPoints(fits_files, output_file, diff='consecutive_diff',
                                    exp_scl=exp_scl, roi=roi, overwrite=overwrite, color_scl=color_scl)
# Select points
select_img_points.select_points()
# Print the path of the output file
print(f'Points saved to {output_file}')