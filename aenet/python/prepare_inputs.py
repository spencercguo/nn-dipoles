import os
import sys
import numpy as np
from math import *
from collections import namedtuple
from scipy.spatial.transform import Rotation as R
from ase import Atoms
from ase.io import write

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
    xsf = [f'# total energy = {dipole}']
    xsf += ['CRYSTAL', 'PRIMVEC']
    for vec in lattice:
        xsf += [f'{vec[0]} {vec[1]} {vec[2]}']
    xsf += ['PRIMCOORD', '{len(xyz)} 1']

    for i in range(len(xyz)):
        if i % 3 == 0:
            sym = 'O'
        else:
            sym = 'H'
        xsf += ['{sym} {xyz[i,0]: .12f} {xyz[i,1]: .12f} {xyz[i,2]: .12f} ']

    output = '\n'.join(xsf)
    with open(name, mode='r') as f:
        f.write(output)

def read_molecular_dipoles(filepath, nsteps):
    dipoles = np.zeros(128, 3, nsteps)
    with open(filepath, mode='r') as f:
        next(f)

        for i in range(nsteps):
            line = next(f)

    return dipoles


def main():
    traj_file = sys.argv[1]
    data_dir = sys.argv[2]

    with open(traj_file) as f:
        xyz = read_xyz(f)[0]
    
    nmol = 128
    # masses in amu for calculating COM
    masses = (15.999, 1.00784, 1.00784)
    # initial lattice vectors (in Angstroms)
    lattice = np.array([[15.660, 0, 0], [0, 15.66, 0], [0, 0, 15.66]])

    # create new rotated file for each atom as center
    for i in range(nmol):
        start_idx = i * 3 # also the coordinates of the oxygen
        r = com(masses, xyz[start_idx:(start_idx + 3)])

        # translate so center of mass of relevant molecule is at origin
        rot_xyz = xyz - r
        rot_lat = lattice - r

        # principle axis goes through oxygen and COM
        # rotate system first so that principle axis aligns with z-axis of box
        R1 = np.zeros((3,3))
        R_2vect(R1, rot_xyz[start_idx], (0, 0, 1))
        rot_xyz = np.matmul(R1, rot_xyz.T).T
        rot_lat = np.matmul(R1, rot_lat)

        # secondary axis goes through hydrogens
        # rotate projection around z-axis so O-H vectors are in xz plane
        # angle in x-y plane
        H_idx = start_idx + 1
        theta = atan(rot_xyz[H_idx,1] / rot_xyz[H_idx,0])
        # rotate about z-axis 
        R2 = R.from_euler('z', -theta)
        rot_xyz = R2.apply(rot_xyz)
        rot_lat = R2.apply(rot_lat)

        # print(com(masses, rot_xyz[start_idx:(start_idx +3)]))
        # print(rot_xyz[H_idx,1])
        # print(rot_xyz[H_idx+1, 1])

        # write rotated xyz to new file for training use
        # atoms = Atoms(symbols=['O','H','H']*nmol, positions=rot_xyz, cell=rot_lat)
        name = f'input_0_{i}'
        full_dir = os.path.abspath(data_dir)
        name = os.path.join(full_dir, name)
        # write(name, atoms, format='xsf')
        
        write_xsf(name, rot_xyz, rot_lat, dipole)


if __name__ == "__main__":
    main()
