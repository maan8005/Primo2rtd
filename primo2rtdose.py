# -*- coding: utf-8 -*-
"""
Created on Sat Apr 10 17:50:54 2026

@author: Maan
"""

"""
Created on Fri Apr 10 14:30:16 2026

Tilte: Convert Primo 3D cube to RT Dose dicom file
@author: Maan Najem
"""
import numpy as np
import pydicom


def create_rtdose(ds, dose_cube, cube_size, voxel_size, image_position):
    """ 
    Method to covert Primo dose file to rt dose dicom file.
    input:
        ds: pydicom object
        dose_cube: Primo dose cube array
        cube_size: size of Primo dose cube in x,y,z direction
        voxel_size: the voxle size of Primo dose cube 
        image_position: initial x,y,z poisition in Primo dose cube.
        
        return an RT dose dicom file saved in the same directory of the python file.
    
    """
    
    ds.DVHSequence = [] # delete TPS DVH files.
    ds.SOPInstanceUID+='.1' #change the UID so file has a unique UID and can be imported into Eclipse TPS 
    dose_cube = dose_cube/ds.DoseGridScaling
    ds.Rows = cube_size[2]
    ds.Columns = cube_size[0]
    ds.NumberOfFrames = cube_size[1]
    ds.PixelSpacing = [voxel_size[0],voxel_size[2]]
    ds.ImagePositionPatient = image_position
    ds.PixelData = dose_cube.astype(np.uint32).tobytes()
    pydicom.write_file('primo_rtdose.dcm', ds)
    return ds
################11############################################################################
def primo_2_rtdose(primo_dose_file, primo_ctvh_file, rtdose_file):
    """ 
    Method to prepare read Primo dose text file and praper it to export as dicom file.
    Input:
        primo_dose_file: path to Primo dose text file
        primo_ctvh_file: path to Primo ctvh file (can be found in Primo project folder).
        rtdose_file: path to rtdose dicom file of the same plan Primo calculated for.
    
    return pydicom rtdose object file which contains Primo dose cube.
    """
    # read RTD dicom file
    ds = pydicom.read_file(rtdose_file)
    
    #read primo ctvh file
    f = open(primo_ctvh_file)
    ctvh = []
    for l in f:
        a = l.split('=')
        ctvh.append(a)
    f.close()
    # dose cube size
    nx = int(ctvh[2][1])
    ny = int(ctvh[3][1])
    nz = int(ctvh[4][1])
    cube_size = [nx,ny,nz]
    # coordinate of first voxel (convert to mm)
    x0 = 10*(float(ctvh[6][1]) - float(ctvh[16][1]))
    y0 = 10*(float(ctvh[8][1]) - float(ctvh[17][1]))
    z0 = 10*(float(ctvh[10][1])- float(ctvh[18][1]))
    image_position = [np.round(x0,3), np.round(z0,3), np.round(y0,3)]
    # voxel size (convert to mm)
    dx = float(ctvh[12][1])*10
    dy = float(ctvh[13][1])*10
    dz = float(ctvh[14][1])*10
    voxel_size = [dx,dy,dz]
    # read primo dose file. 
    dose = np.loadtxt(primo_dose_file, skiprows=18, comments='#')[:,0]
    # convert to 3d dose cube 
    dose_sorted = np.zeros([ny, nz, nx])
    m = 0
    for i in range(nz):
        for j in range(ny):
            for k in range(nx):
                dose_sorted[j,i,k] = dose[m]
                m+=1
    
    
    # Covert primo dose to rt dose dicom file 
    ds = create_rtdose(ds, dose_sorted[::-1,:,:],cube_size, voxel_size, image_position)
    return ds


# How to use  

# rt dose file path
rtdose_file = r'path to rt dose dicom file' 
# primo dose file path
primo_dose_file = r'path ro primo dose cube text file'
# primo ctvh file path
primo_ctvh_file= r'path to primo ctvh file' 

ds = primo_2_rtdose(primo_dose_file, primo_ctvh_file, rtdose_file)



