import os
import sys
import numpy as np
from math import isclose

for i in range(127):
    filepath = f'../input/input_0_{i}.xsf'
    o_index = 11 + i * 3
    h1_index = o_index + 1
    h2_index = o_index + 2
    
    with open(filepath) as f:
        lines = f.readlines()
        ox, oy, oz = lines[o_index].split()[1:]
        assert float(ox) == 0
        assert float(oy) == 0

        h1y = lines[h1_index].split()[2]
        h2y = lines[h2_index].split()[2]
        assert float(h1y) == 0
        assert float(h2y) == 0
        
        lat_vec1 = list(map(float, lines[5].split()))
        lat_vec2 = list(map(float, lines[6].split()))
        lat_vec3 = list(map(float, lines[7].split()))
        
        assert isclose(np.dot(lat_vec1, lat_vec2), 0, abs_tol=1e-5)
        assert isclose(np.dot(lat_vec2, lat_vec3), 0, abs_tol=1e-5)
        assert isclose(np.linalg.norm(lat_vec1), 15.66, abs_tol=1e-5)
        assert isclose(np.linalg.norm(lat_vec2), 15.66, abs_tol=1e-5)
        assert isclose(np.linalg.norm(lat_vec3), 15.66, abs_tol=1e-5)
