# This file contains useful functions for file I/O and rotations.

import numpy as np
from math import *
from collections import namedtuple
from scipy.spatial.transform import Rotation as R

def read_xyz(fin):
    """ 
    read a xyz file from file handle
    Parameters
    ----------
    fin : file handle
    file to read from
    Returns
    -------
    fin : open file
    xyz : namedtuple
    returns a named tuple with coords, title and list of atomtypes.
    See Also
    --------
    write_xyz
    """
    natoms = int(fin.readline())
    title = fin.readline()[:-1]
    coords = np.zeros([natoms, 3], dtype="float64")
    atomtypes = []
    for x in coords:
        line = fin.readline().split()
        atomtypes.append(line[0])
        x[:] = list(map(float, line[1:4]))

    return namedtuple("XYZFile", ["coords", "title", "atomtypes"]) \
                (coords, title, atomtypes)

def R_2vect(R, vector_orig, vector_fin):
    """Calculate the rotation matrix required to rotate from one vector to another.
    For the rotation of one vector to another, there are an infinit series of rotation matrices
    possible.  Due to axially symmetry, the rotation axis can be any vector lying in the symmetry
    plane between the two vectors.  Hence the axis-angle convention will be used to construct the
    matrix with the rotation axis defined as the cross product of the two vectors.  The rotation
    angle is the arccosine of the dot product of the two unit vectors.
    Given a unit vector parallel to the rotation axis, w = [x, y, z] and the rotation angle a,
    the rotation matrix R is::
              |  1 + (1-cos(a))*(x*x-1)   -z*sin(a)+(1-cos(a))*x*y   y*sin(a)+(1-cos(a))*x*z |
        R  =  |  z*sin(a)+(1-cos(a))*x*y   1 + (1-cos(a))*(y*y-1)   -x*sin(a)+(1-cos(a))*y*z |
              | -y*sin(a)+(1-cos(a))*x*z   x*sin(a)+(1-cos(a))*y*z   1 + (1-cos(a))*(z*z-1)  |
    @param R:           The 3x3 rotation matrix to update.
    @type R:            3x3 numpy array
    @param vector_orig: The unrotated vector defined in the reference frame.
    @type vector_orig:  numpy array, len 3
    @param vector_fin:  The rotated vector defined in the reference frame.
    @type vector_fin:   numpy array, len 3
    """

    # Convert the vectors to unit vectors.
    vector_orig = vector_orig / np.linalg.norm(vector_orig)
    vector_fin = vector_fin / np.linalg.norm(vector_fin)

    # The rotation axis (normalised).
    axis = np.cross(vector_orig, vector_fin)
    axis_len = np.linalg.norm(axis)
    if axis_len != 0.0:
        axis = axis / axis_len

    # Alias the axis coordinates.
    x = axis[0]
    y = axis[1]
    z = axis[2]

    # The rotation angle.
    angle = acos(np.dot(vector_orig, vector_fin))

    # Trig functions (only need to do this maths once!).
    ca = cos(angle)
    sa = sin(angle)

    # Calculate the rotation matrix elements.
    R[0,0] = 1.0 + (1.0 - ca)*(x**2 - 1.0)
    R[0,1] = -z*sa + (1.0 - ca)*x*y
    R[0,2] = y*sa + (1.0 - ca)*x*z
    R[1,0] = z*sa+(1.0 - ca)*x*y
    R[1,1] = 1.0 + (1.0 - ca)*(y**2 - 1.0)
    R[1,2] = -x*sa+(1.0 - ca)*y*z
    R[2,0] = -y*sa+(1.0 - ca)*x*z
    R[2,1] = x*sa+(1.0 - ca)*y*z
    R[2,2] = 1.0 + (1.0 - ca)*(z**2 - 1.0)

def com(m, r):
    """
    Calculate COM for a series of masses m
    at positions r.
    
    m is an array of masses of length n
    r is an array of positions of size n x 3
    """
    return np.dot(m, r) / np.sum(m)

def write_xsf(name, xyz, lat, dipole):
    xsf = [f'# total energy = {dipole}', '']
    xsf += ['CRYSTAL', '', 'PRIMVEC']
    for vec in lat:
        xsf += [f'{vec[0]} {vec[1]} {vec[2]}']
    xsf += ['']
    xsf += ['PRIMCOORD', f'{len(xyz)} 1']

    for i in range(len(xyz)):
        if i % 3 == 0:
            sym = 'O'
        else:
            sym = 'H'
        xsf += [f'{sym} {xyz[i,0]: .12f} {xyz[i,1]: .12f} {xyz[i,2]: .12f} 0.0 0.0 0.0']

    output = '\n'.join(xsf)
    with open(name, mode='w') as f:
        f.write(output)

def read_molecular_dipoles(filepath, nsteps):
    """
    Read molecular dipole file with DFT information
    for a specified number of time steps.
    """
    dipoles = np.zeros((128, 3, nsteps))
    with open(filepath, mode='r') as f:
        for i in range(nsteps):
            next(f) # skip line with headers
            for j in range(128):
                line = next(f)
                dipoles[j,:,i] = (float(line.split()[2]), float(line.split()[3]),
                    float(line.split()[4]))

    return dipoles



