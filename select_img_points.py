# class that takes an input list of .fits files paths  and for each file, one at a time:
# 1- Read file as Sunpy MAPS object and plots it on screen using Sunpy built in functions (depending on the instrument specified in fits header)
# 2- Allows the user to click on the image to select points
# 3- Converts the selected pixel values to Carrington coordinates using the WCS information in the .fits file and Sunpy built in functions
# 4- Saves the selected points to a .csv file

import sunpy.map
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from astropy import units as u
from astropy.coordinates import SkyCoord
import matplotlib.colors as colors
import os

class SelectImgPoints:
    def __init__(self, fits_files, output_file, diff='none', coord_type='heliographic_stonyhurst', roi=None,
                 overwrite=False, color_scl=None, exp_scl=None, norm_exp=True): # heliographic_carrington or heliographic_stonyhurst
        '''
        Parameters
        ----------
        fits_files : list
            List of .fits files paths to be processed.
        output_file : str
            Path to the output .csv file where the selected points will be saved.
        diff : str, optional
            use running difference images, options are
            'diff' : substract two consecutive files and computes the difference before plotting and selecting points
            'consecutive_diff' : substract two consecutive files and computes the difference before plotting and selecting points
            'none' : no difference is computed, by default 'none'
        coord_type : str, optional
            Coordinate system to use, by default 'heliographic_stonyhurst'
        roi : list, optional
            Region of interest in arcsec [top_right_x, top_right_y, bottom_left_x, bottom_left_y], by default None
        overwrite : bool, optional
            If True, the output file will be overwritten if it already exists, by default False
        color_scl : int, optional
            Number of sigmas to control image color scale range, by default None
        exp_scl : float, optional
            Exponential scaling factor for the image, by default None    
        norm_exp : bool, optional
            If True, the image is normalized with the exposure time included in its fits header (xposure)   
        '''
        self.fits_files = fits_files
        self.output_file = output_file
        self.points = []
        self.diff = diff
        self.coord_type = coord_type
        self.roi = roi
        self.overwrite = overwrite
        self.color_scl = color_scl
        self.exp_scl = exp_scl
        self.norm_exp = norm_exp
        # create odirectory if it does not exist
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        if os.path.isfile(self.output_file) and not self.overwrite:
            print(f'Error: File {self.output_file} already exists. Use overwrite=True to overwrite it')
            os._exit(0)        

    def select_points(self):
        if self.diff=='diff':
        # if diff, then substract two consecutive files and computes the difference before plotting and selecting points
        # each file is used one time 
            for i in range(len(self.fits_files)//2-1):
                print('Processing case '+ str(i+1) + ' of ' + str(len(self.fits_files)//2-1))
                print('Images: ' + os.path.basename(self.fits_files[2*i]) + ' and ' + os.path.basename(self.fits_files[2*i+1]))
                # Read the .fits file as a Sunpy MAPS object
                map_seq = sunpy.map.Map([self.fits_files[2*i], self.fits_files[2*i+1]], sequence=True)
                #checks compatible image sizes
                if map_seq[0].data.shape != map_seq[1].data.shape:
                    print(f'Warning: {self.fits_files[2*i]} and {self.fits_files[2*i+1]} have different image sizes')
                    # resamples to match the smallest image
                    if map_seq[0].data.shape[0] < map_seq[1].data.shape[0]:
                        res_map1 = map_seq[1].resample(map_seq[0].data.shape * u.pixel)
                        map_seq = sunpy.map.Map([map_seq[0], res_map1], sequence=True)
                    else:
                        res_map0 = map_seq[0].resample(map_seq[1].data.shape * u.pixel)
                        map_seq = sunpy.map.Map([res_map0,map_seq[1]], sequence=True)                                              
                # Plot the image
                if self.norm_exp:
                    print('Normalizing by exposure times:')
                    print(map_seq[0].exposure_time.value, map_seq[1].exposure_time.value)
                    map_seq_0_scl = sunpy.map.Map(map_seq[0].data/map_seq[0].exposure_time.value, map_seq[0].meta)
                    map_seq_1_scl = sunpy.map.Map(map_seq[1].data/map_seq[1].exposure_time.value, map_seq[1].meta)
                    map_seq = sunpy.map.Map([map_seq_0_scl,map_seq_1_scl], sequence=True)                   
                if self.exp_scl is not None:
                    map_seq_0_scl = sunpy.map.Map(map_seq[0].data**self.exp_scl, map_seq[0].meta)
                    map_seq_1_scl = sunpy.map.Map(map_seq[1].data**self.exp_scl, map_seq[1].meta)
                    map_seq = sunpy.map.Map([map_seq_0_scl,map_seq_1_scl], sequence=True)                 
                # uses the name of the two files to name the plot
                title = self.fits_files[2*i+1].split('/')[-1]  + ' - ' +  self.fits_files[2*i].split('/')[-1] 
                map = sunpy.map.Map(map_seq[1].quantity - map_seq[0].quantity, map_seq[0].meta)
                # if roi is specified, plot only that portion of the map
                if self.roi is not None:
                    top_right = SkyCoord(self.roi[0]*u.arcsec, self.roi[1]*u.arcsec, frame=map.coordinate_frame)
                    bottom_left = SkyCoord(self.roi[2]*u.arcsec, self.roi[3]*u.arcsec, frame=map.coordinate_frame)
                    map = map.submap(bottom_left, top_right=top_right)
                    print(f'Warning: ROI box [arcsec] specified. Plotting only the portion of the image within the box {self.roi}')
                m = np.mean(map.data)
                sd = np.std(map.data)
                if self.color_scl is None: 
                    scl = 3
                else:
                    scl = self.color_scl                 
                # plots with white as max and black as min
                map.plot(norm=colors.Normalize(vmin=m-scl*sd, vmax=m+scl*sd), cmap='gray', title=title)
                # Allow the user to click on the image to select points
                points = plt.ginput(n=-1, timeout=0)
                # Convert the selected pixel values to Carrington coordinates using the WCS information in the .fits file and Sunpy built in functions
                wcs = map.wcs
                wcs_points= [wcs.pixel_to_world(j[0], j[1]) for j in points]
                carrington_points = [SkyCoord(j.Tx, j.Ty, frame=self.coord_type, obstime=map.date) for j in wcs_points]
                carrington_lon = [j.lon.arcsec for j in carrington_points]
                carrington_lat = [j.lat.arcsec for j in carrington_points]
                # Save the selected points to a common list including the file basename
                self.points.append([self.fits_files[2*i].split('/')[-1], carrington_lon, carrington_lat])
                plt.close()
        elif self.diff=='consecutive_diff':
        # if diff, then substract two consecutive files and computes the difference before plotting and selecting points
        # each file is used two times
            for i in range(len(self.fits_files)-1):
                print('Procesing case '+ str(i+1) + ' of ' + str(len(self.fits_files)-1))
                print('Images: ' + os.path.basename(self.fits_files[i]) + ' and ' + os.path.basename(self.fits_files[i+1]))
                # Read the .fits file as a Sunpy MAPS object
                map_seq = sunpy.map.Map([self.fits_files[i], self.fits_files[i+1]], sequence=True)
                #checks compatible image sizes
                if map_seq[0].data.shape != map_seq[1].data.shape:
                    print(f'Warning: {self.fits_files[i]} and {self.fits_files[i+1]} have different image sizes')
                    # resamples to match the smallest image
                    if map_seq[0].data.shape[0] < map_seq[1].data.shape[0]:
                        res_map1 = map_seq[1].resample(map_seq[0].data.shape * u.pixel)
                        map_seq = sunpy.map.Map([map_seq[0], res_map1], sequence=True)
                    else:
                        res_map0 = map_seq[0].resample(map_seq[1].data.shape * u.pixel)
                        map_seq = sunpy.map.Map([res_map0,map_seq[1]], sequence=True)                                              
                # Plot the image
                if self.norm_exp:
                    print('Normalizing by exposure times:')
                    print(map_seq[0].exposure_time.value, map_seq[1].exposure_time.value)
                    map_seq_0_scl = sunpy.map.Map(map_seq[0].data/map_seq[0].exposure_time.value, map_seq[0].meta)
                    map_seq_1_scl = sunpy.map.Map(map_seq[1].data/map_seq[1].exposure_time.value, map_seq[1].meta)
                    map_seq = sunpy.map.Map([map_seq_0_scl,map_seq_1_scl], sequence=True)                    
                if self.exp_scl is not None:
                    map_seq_0_scl = sunpy.map.Map(map_seq[0].data**self.exp_scl, map_seq[0].meta)
                    map_seq_1_scl = sunpy.map.Map(map_seq[1].data**self.exp_scl, map_seq[1].meta)
                    map_seq = sunpy.map.Map([map_seq_0_scl,map_seq_1_scl], sequence=True)         
                # uses the name of the two files to name the plot
                title = self.fits_files[i+1].split('/')[-1]  + ' - ' +  self.fits_files[i].split('/')[-1] 
                map = sunpy.map.Map(map_seq[1].quantity - map_seq[0].quantity, map_seq[0].meta)
                # if roi is specified, plot only that portion of the map
                if self.roi is not None:
                    top_right = SkyCoord(self.roi[0]*u.arcsec, self.roi[1]*u.arcsec, frame=map.coordinate_frame)
                    bottom_left = SkyCoord(self.roi[2]*u.arcsec, self.roi[3]*u.arcsec, frame=map.coordinate_frame)
                    map = map.submap(bottom_left, top_right=top_right)
                    print(f'Warning: ROI box [arcsec] specified. Plotting only the portion of the image within the box {self.roi}')
                m = np.mean(map.data)
                sd = np.std(map.data)
                if self.color_scl is None: 
                    scl = 3
                else:
                    scl = self.color_scl 
                # plots with white as max and black as min
                map.plot(norm=colors.Normalize(vmin=m-scl*sd, vmax=m+scl*sd), cmap='gray', title=title)
                # Allow the user to click on the image to select points
                points = plt.ginput(n=-1, timeout=0)
                # Convert the selected pixel values to Carrington coordinates using the WCS information in the .fits file and Sunpy built in functions
                wcs = map.wcs
                wcs_points= [wcs.pixel_to_world(j[0], j[1]) for j in points]
                carrington_points = [SkyCoord(j.Tx, j.Ty, frame=self.coord_type, obstime=map.date) for j in wcs_points]
                carrington_lon = [j.lon.arcsec for j in carrington_points]
                carrington_lat = [j.lat.arcsec for j in carrington_points]
                # Save the selected points to a common list including the file basename
                self.points.append([self.fits_files[i].split('/')[-1], carrington_lon, carrington_lat])
                plt.close()           
        elif self.diff=='none':
            for fits_file in self.fits_files:
                print('Procesing case '+ str(self.fits_files.index(fits_file)+1) + ' of ' + str(len(self.fits_files)))
                print('Image: ' + os.path.basename(fits_file))
                # Read the .fits file as a Sunpy MAPS object
                map = sunpy.map.Map(fits_file)
                # Plot the image
                if self.norm_exp:
                    print('Normalizing by exposure time:')
                    print(map.exposure_time.value)
                    map = map.data/map.exposure_time.value
                    map = sunpy.map.Map(map, map.meta)                   
                if self.exp_scl is not None:
                    map = map.data**self.exp_scl
                    map = sunpy.map.Map(map, map.meta)                 
                map.plot()
                # Allow the user to click on the image to select points
                points = plt.ginput(n=-1, timeout=0)
                # Convert the selected pixel values to Carrington coordinates using the WCS information in the .fits file and Sunpy built in functions
                wcs = map.wcs
                wcs_points= [wcs.pixel_to_world(i[0], i[1]) for i in points]
                carrington_points = [SkyCoord(i.Tx, i.Ty, frame=self.coord_type, obstime=map.date) for i in wcs_points]
                carrington_lon = [i.lon.arcsec for i in carrington_points]
                carrington_lat = [i.lat.arcsec for i in carrington_points]
                # Save the selected points to a common list including the file basename
                self.points.append([fits_file.split('/')[-1], carrington_lon, carrington_lat])
                plt.close()             
        else:
            print('Error: diff parameter must be either "diff", "consecutive_diff" or "none"')
            os._exit(0)
        # Save the selected points to a .csv file               
        df = pd.DataFrame(self.points, columns=['file', 'lon [arcsec]', 'lat [arcsec]'])
        df.to_csv(self.output_file, index=False)            