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
points_list = repo_path + '/output/selected_points_id02.csv'
output_dir = repo_path + '/output/plots'
#####
print('Computing derived quantities...')

output_dir += '/' + os.path.basename(points_list).split('.')[0]
os.makedirs(output_dir, exist_ok=True)
# reads csv ith  ['file', 'lon [arcsec]', 'lat [arcsec]']
points = pd.read_csv(points_list)
# gets date from file name
points['date'] = points['file'].str.split('_').str[-2].str[0:15]
# converts date to timestamp
points['date'] = pd.to_datetime(points['date'])
# sort by date
points = points.sort_values(by='date')
# get lat and lon
lat = points['lat [arcsec]'].values
lon = points['lon [arcsec]'].values
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
    # computes the angular width between the first and third point
    aw.append(np.abs(np.arctan2(np.sin(all_lon[0] - all_lon[2]), np.cos(all_lon[0] - all_lon[2])))*180/np.pi)
    # computes the gometric distance of the center point
    h.append(np.sqrt(all_lat[1]**2 + all_lon[1]**2))

print('Plotting...')
# plot aw vs date to png file
fig = plt.figure()
plt.plot(points['date'], aw,'.--k')
plt.xticks(rotation=45)
plt.ylabel('Angular width [deg]')
plt.xlabel('Date')
plt.title('Angular width vs Date')
plt.tight_layout()
plt.grid()
plt.savefig(output_dir + '/aw_vs_date.png')
plt.close()

# plot h vs date to png file
fig = plt.figure()
plt.plot(points['date'], h,'.--k')
plt.xticks(rotation=45)
plt.ylabel('Height [arcsec]')
plt.xlabel('Date')
plt.title('Height vs Date')
plt.tight_layout()
plt.grid()
plt.savefig(output_dir + '/h_vs_date.png')
plt.close()


