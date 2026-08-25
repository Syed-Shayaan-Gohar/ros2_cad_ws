# The stl files I exported from Fusion 360 were too large, even at low refinement settings
# This script takes those files and decimates them to ensure smooth renfering

import pymeshlab
import glob
import os


for filepath in glob.glob("meshes/*.stl"):
    print(filepath)
    ms = pymeshlab.MeshSet()
    ms.load_new_mesh(filepath)
    ms.meshing_decimation_quadric_edge_collapse(
        targetfacenum = 15000,  # absolute face count to reduce to
        preservenormal = True,  # keeps shading looking correct
        preservetopology = True,  # avoids introducing holes/non-manifold geometry
        planarquadric = True  # better preserves flat surfaces (good for chassis-like parts)
    )
    dir_name, file_name = os.path.split(filepath)
    new_file_name = "decimated_"+file_name
    new_file_path = "decimated_meshes/"+new_file_name
    ms.save_current_mesh(new_file_path)

