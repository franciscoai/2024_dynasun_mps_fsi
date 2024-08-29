'''
Reads /output/selected_points.csv and computes and plots some derived quantities
'''
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import matplotlib as mpl
mpl.use('Agg')

#CONSTANTS
repo_path = os.getcwd()
points_list_path = repo_path + '/output' # it process all csv files in this directory
output_dir = repo_path + '/output/plots' # output directory for plots
solar_rad_in_m = 6.957e8 # solar radius in meters
#####
# finds al csv files in points_list_path
points_lists = [f for f in os.listdir(points_list_path) if f.endswith('.csv')]
points_lists = [os.path.join(points_list_path, f) for f in points_lists]
# process each csv file
for points_list in points_lists:
    print('Computing derived quantities for file: ' + os.path.basename(points_list))
    curr_output_dir = output_dir + '/' + os.path.basename(points_list).split('.')[0]
    os.makedirs(curr_output_dir, exist_ok=True)
    # reads csv ith  ['file', 'lon [arcsec]', 'lat [arcsec]']
    points = pd.read_csv(points_list)
    # gets date from file name
    points['date'] = points['file'].str.split('_').str[-2].str[0:15]
    # converts date to timestamp
    points['date'] = pd.to_datetime(points['date'])
    # sort by date
    points = points.sort_values(by='date')
    # remove points with lat or lon that contains only '[]' (are empty)
    points = points[~points['lat [arcsec]'].str.contains('\[\]')]
    # get lat and lon
    lat = points['lat [arcsec]'].values
    lon = points['lon [arcsec]'].values
    # get distance to the sun in [m] from dsun column
    dsun = points['dsun [m]'].values
    h=[]
    aw=[]
    for i in range(0,len(lat)):
        # extracts from lat string the csv values
        all_lat=str.split(lat[i],'[')[-1]
        all_lat=str.split(all_lat,']')[0]
        all_lat=np.array(str.split(all_lat,',')).astype(float)
        # extracts from lon string the csv values
        all_lon=str.split(lon[i],'[')[-1]
        all_lon=str.split(all_lon,']')[0]
        all_lon=np.array(str.split(all_lon,',')).astype(float)
        # converts all points to polar coordinates
        all_phi = np.arctan2(all_lat, all_lon)
        all_r = np.sqrt(all_lat**2 + all_lon**2)
        # computes the angular width between the first and third point
        aw.append(np.abs(all_phi[0]-all_phi[2])*180/np.pi)
        # converts all_r[1] from arcsec to solar radii
        h_rsun = np.deg2rad(all_r[1]/3600)*dsun[i]/solar_rad_in_m
        h.append(h_rsun)

    print('Plotting...')
    # plot aw vs date to png file
    fig = plt.figure()
    plt.plot(points['date'], aw,'o--k')
    plt.xticks(rotation=45)
    plt.ylabel('Angular width [deg]')
    plt.xlabel('Date')
    plt.title('Angular width vs Date')
    plt.tight_layout()
    plt.grid()
    plt.savefig(curr_output_dir + '/aw_vs_date.png')
    plt.close()

    # plot h vs date to png file
    fig = plt.figure()
    plt.plot(points['date'], h,'o--k')
    plt.xticks(rotation=45)
    plt.ylabel('Height [Rs]')
    plt.xlabel('Date')
    plt.title('Height vs Date')
    plt.tight_layout()
    plt.grid()
    plt.savefig(curr_output_dir + '/h_vs_date.png')
    plt.close()


