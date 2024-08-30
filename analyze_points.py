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
points_lists = sorted([os.path.join(points_list_path, f) for f in points_lists])
# variables to plot together for all csv files
all_mean_dawdh = []  
all_mean_spped = []
all_mean_aw = []
all_aw_fit_par = []
all_aw_and_h = []
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
        if all_phi[0]*all_phi[2] > 0:
            aw.append(np.abs(all_phi[0]-all_phi[2])*180/np.pi)
        else:
            abs_sum = np.abs(np.abs(all_phi[2]) + np.abs(all_phi[0])) 
            if abs_sum > np.pi:
                aw.append(np.abs(abs_sum - 2*np.pi)*180/np.pi)
            else:
                aw.append(abs_sum*180/np.pi)
            
        # converts all_r[1] from arcsec to solar radii
        h_rsun = np.deg2rad(all_r[1]/3600)*dsun[i]/solar_rad_in_m
        h.append(h_rsun)

    event_id = str.split(os.path.basename(curr_output_dir),'_')[-1]
    all_mean_aw.append([event_id, np.mean(aw)])

    # if event_id == 'id01':
    #     breakpoint()
    
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

    # plot velocity in km/s vs date to png file
    fig = plt.figure()
    h_km = np.array(h)*solar_rad_in_m/1e3
    date_diff_sec = np.diff(points['date']).astype('timedelta64[s]').astype(int)
    speed = np.diff(h_km)/date_diff_sec
    all_mean_spped.append([event_id, np.mean(speed)])
    plt.plot(points['date'][1:], speed,'o--k')
    plt.xticks(rotation=45)
    plt.ylabel('Speed [km/s]')
    plt.xlabel('Date')
    plt.title('Speed vs Date')
    plt.tight_layout()
    plt.grid()
    plt.savefig(curr_output_dir + '/speed_vs_date.png')

    # plot aw vs h to png file
    fig = plt.figure()
    plt.plot(h, aw,'o--k')
    # fit and plot a line
    m, b = np.polyfit(h, aw, 1)
    all_aw_fit_par.append([event_id, m, b])
    plt.plot(h, m*np.array(h) + b, 'r',label='y = ' + str(round(m,2)) + 'x + ' + str(round(b,2)))
    plt.ylabel('Angular width [deg]')
    plt.xlabel('Height [Rs]')
    plt.title('Angular width vs Height')
    plt.tight_layout()
    plt.grid()
    plt.legend()
    plt.savefig(curr_output_dir + '/aw_vs_h.png')
    plt.close()

    # plot derivative of aw wrt h vs h
    fig = plt.figure()
    dawdh = np.diff(aw)/np.diff(h)
    all_mean_dawdh.append([event_id, np.mean(dawdh)])
    plt.plot(h[1:], dawdh,'o--k')
    plt.ylabel('d(aw)/dh [deg/Rs]')
    plt.xlabel('Height [Rs]')
    plt.title('d(aw)/dh vs Height')
    plt.tight_layout()
    plt.grid()
    plt.savefig(curr_output_dir + '/dawdh_vs_h.png')
    plt.close()

    all_aw_and_h.append([event_id, h, aw])

#common plots
# plot all mean speed vs event_id
fig = plt.figure()
all_mean_spped = np.array(all_mean_spped)   
plt.plot(all_mean_spped[:,0], all_mean_spped[:,1].astype(float),'o--k')
plt.xticks(rotation=45)
plt.ylabel('Mean Speed [km/s]')
plt.xlabel('Event ID')
plt.title('Mean Speed vs Event ID')
plt.tight_layout()
plt.grid()
plt.savefig(output_dir + '/mean_speed_vs_event_id.png')
plt.close()

# plot all mean aw vs event_id
fig = plt.figure()
all_mean_aw = np.array(all_mean_aw)
plt.plot(all_mean_aw[:,0], all_mean_aw[:,1].astype(float),'o--k')
plt.xticks(rotation=45)
plt.ylabel('Mean Angular width [deg]')
plt.xlabel('Event ID')
plt.title('Mean Angular width vs Event ID')
plt.tight_layout()
plt.grid()
plt.savefig(output_dir + '/mean_aw_vs_event_id.png')
plt.close()

#plot all all_aw_fit_par vs event_id
fig = plt.figure()
all_aw_fit_par = np.array(all_aw_fit_par)
plt.plot(all_aw_fit_par[:,0], all_aw_fit_par[:,1].astype(float),'o--k',label='m')
plt.plot(all_aw_fit_par[:,0], all_aw_fit_par[:,2].astype(float),'o--r',label='b')
plt.xticks(rotation=45)
plt.ylabel('Fit parameters')
plt.xlabel('Event ID')
plt.title('Fit parameters vs Event ID')
plt.tight_layout()
plt.grid()
plt.legend()
plt.savefig(output_dir + '/fit_par_vs_event_id.png')
plt.close()

# scatter plot of all_aw_fit_par[:,1] vs all_aw_fit_par[:,2]
fig = plt.figure()
plt.scatter(all_aw_fit_par[:,1].astype(float), all_aw_fit_par[:,2].astype(float))
m, b = np.polyfit(all_aw_fit_par[:,1].astype(float), all_aw_fit_par[:,2].astype(float), 1)
plt.plot(all_aw_fit_par[:,1].astype(float), m*all_aw_fit_par[:,1].astype(float) + b, 'r',label='y = ' + str(round(m,2)) + 'x + ' + str(round(b,2)))
plt.ylabel('b')
plt.xlabel('m')
plt.title('b vs m')
plt.tight_layout()
plt.grid()
plt.legend()
plt.savefig(output_dir + '/b_vs_m.png')
plt.close()

# scatter plot of all_aw_fit_par[:,1] vs all_aw_fit_par[:,2]
fig = plt.figure()
ho=np.abs(m)+1
aw_at_1rs = all_aw_fit_par[:,1].astype(float)*ho + all_aw_fit_par[:,2].astype(float)
plt.scatter(all_aw_fit_par[:,1].astype(float), aw_at_1rs)
# fits a line
m, b = np.polyfit(all_aw_fit_par[:,1].astype(float), aw_at_1rs, 1)
plt.plot(all_aw_fit_par[:,1].astype(float), m*all_aw_fit_par[:,1].astype(float) + b, 'r',label='y = ' + str(round(m,2)) + 'x + ' + str(round(b,2))) 
# ho in ther labels with decimal 2 digits
plt.ylabel('aw at h0=%s Rs [deg]' % str(round(ho,2)))
plt.xlabel('mean daw/dh [deg/Rs]')
plt.tight_layout()
plt.legend()
plt.grid()
plt.savefig(output_dir + '/aw_at_%s_vs_dawdh.png' % str(round(ho,2)))
plt.close()

# all_aw_and_h i a sinlge plot
fig = plt.figure()
for i in range(0,len(all_aw_and_h)):
    plt.plot(all_aw_and_h[i][1], all_aw_and_h[i][2],'o',label=all_aw_and_h[i][0])
plt.ylabel('Angular width [deg]')
plt.xlabel('Height [Rs]')
plt.title('Angular width vs Height')
plt.legend()
h=np.linspace(0.5,2.4,10)
for i in range(0,len(all_aw_and_h)):
    m = all_aw_fit_par[i][1].astype(float)
    b = all_aw_fit_par[i][2].astype(float)
    plt.plot(h, m*h+ b, label=all_aw_and_h[i][0],linewidth=0.5)
plt.ylabel('Angular width [deg]')
plt.xlabel('Height [Rs]')
plt.title('Angular width vs Height')
plt.tight_layout()
plt.grid()
plt.savefig(output_dir + '/all_aw_vs_h_fit_lines.png')
plt.close()



