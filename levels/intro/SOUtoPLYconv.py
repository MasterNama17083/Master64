#!/usr/bin/env python

"""
    2020-08-01
    Version 2.0.1
    A .sou to .ply exporter
    SOU seems to be mostly C (or C++?) instructions to load models, lights and
    animations in an N64 game, as some things can be matched to N64
    documentation found online
    FIXES (from 2.0):
        - Some dumb code broke some model names and became unwritable
        - Can open shape files (with bugs most likely)
        - Better model detection thanks to the power of regex
    FIXES (from 1.5):
        - Revamped the model reader, old reader added all vertex data to all 
          the models which looked like a cloud of points when imported to 
          blender, new reader doesn't this makes models smaller and easier 
          to handle.
        - Added vertex color but see TODO notes.
    TODO:
        - Smoothing groups (I think ply doesn't support it)
        - Vertex color works but some models (normally textured models) lack 
          light information so I don't know how to calculate those maybe someone 
          can help
        - Some sou files that start with gfx are collections of other sou files
          and textures. Need to work on importing those, specially because they
          have light information sometimes check gfx_mario.sou, this is why in 
          this version at least light_mario is hardcoded.
"""

import sys
import os
import struct
import re

# Detects where models are
gfx_re = re.compile("(static )?(Gfx )\S* ?\[\] ?= ?{")

# Light storage
lights_dict = {'light_mario': [[0, 0, 255], [255, 0, 0], [255, 255, 255], 
                               [114, 28, 14], [254, 193, 121], [115, 6, 0]]
                }

def to_float(x,e,inv=False):
    """ Converts m.n precision numbers to python floats
        The N64 uses 10.5 precision for storing UV information in vertices
    """
    c = abs(x)
    sign = 1
    if x < 0:
        # convert back from two's complement
        c = x - 1
        c = ~c
        sign = -1
    f = (1.0 * c) / (2 ** e)
    f = f * sign
    if inv:
        f = f * -1
        f = f + 32
    return st_coord(f)

def xyz_coord(c):
    """ Converts integer numbers to plane coordinates
        The N64 uses a 8-bit signed integer (-128 to 127) to store vertex coords
        What we need to do is divide by 128 to obtain the correct coordinate
    """
    return float(c)/128

def st_coord(c, sz=32):
    """ Obtains the UV coordinate
        Here I assume that the texture is 32x32 pixels in size adapt accordingly
    """
    return float(c)/sz

def sou_to_file(file):
    """ Exports a .sou file to multiple .ply files (hopefully)
    """
    f = open(file, 'r')
    SR = 0 # Vertex loading state
    GR = 0 # Model loading state
    LR = 0 # Light loading state
    triOff = 0 # triangle offset
    curLGT = -1 # current geometry light index
    mname = '' # current model name
    vname = '' # current vertex data name
    lname = '' # current lights loaded
    tmpname = '' # current name of the lights we're loading in LR state
    model_dict = {} # models storage
    vertex_dict = {} # vertex storage
    voff = -1 # vertex offset 
    loaded_vertex = '' # name of the current list of vertices
    blklist = ['=','{','}','[',']'] # Some unwanted characters to clean some strings
    for x in f:
        # Model loading state
        if GR:
            if x.find("gsSPLight(")>=0:
                lname = x[x.find('&')+1:x.find('[')]
                curLGT = int(x[x.find("[")+1:x.find("]")])
            elif x.find("gsSPVertex(")>=0:
                voff = len(model_dict[mname]['v'])
                rng = x[x.find("[")+1:x.find("]")]
                # For some reason some gsSPVertex have substractions ?
                rng = rng.split("-")
                if len(rng) > 1:
                    triOff = int(rng[0]) - int(rng[1])
                else:
                    triOff = int(rng[0])
                name = x[x.find('&')+1:x.find('[')]
                loaded_vertex = name 
            elif x.find("gsSP1Triangle(")>=0:
                tr = x.replace("\tgsSP1Triangle(","").replace("),\n","").split(',')
                tr.pop()
                tf = []
                for t in tr:
                    ori = int(t) + voff
                    t = int(t) + triOff
                    if curLGT > -1 and lname != '':
                        curr_light = lights_dict[lname][curLGT]
                        vertex_dict[loaded_vertex][t][6+0] = curr_light[0]
                        vertex_dict[loaded_vertex][t][6+1] = curr_light[1]
                        vertex_dict[loaded_vertex][t][6+2] = curr_light[2]
                    if not ori in model_dict[mname]['v']:
                        model_dict[mname]['v'][ori] = vertex_dict[loaded_vertex][t]
                    tf.append(ori)
                model_dict[mname]['t'].append(tf)
                model_dict[mname]['tt'] += 1
        # Vertex loading state
        if SR:
            vtmp = x[x.find('{')+1:x.find('}')].replace(' ','').split(',')
            vertex_dict[vname].append(vtmp) 
        # Lights loading state
        if LR:
            if '};' not in x:
                lights_dict[tmpname].append([int(l) for l in x[x.find('(')+1:x.find(')')].split(',')])
        if gfx_re.match(x):
            """ Most models in the sou format start with this line
                when we find this line, the model loading state needs to 
                be activated to start "executing" the model commands
            """
            print(x)
            # Activate model loading state
            GR = 1 
            # Get the model name
            mname = x[x.find("Gfx")+4:x.find("[")]
            mname = mname.strip()
            print(mname)
            # Create a new model in our model storage
            model_dict[mname] = {'v':{}, 't':[], 'tt':0} 
        if x.find('Lights1') >= 0 :
            """ Lights seem to be identified by this line
                So lets enter the light loading state to get the lights
            """
            # Get the lights name
            tmpname = x.replace("Lights1","").replace("static","")
            tmpname = ''.join([c for c in tmpname if c not in blklist]).strip()
            # Add a new entry in our light storage
            lights_dict[tmpname] = []
            LR = 1 # enter light loading state
        if x.find('static Vtx') >= 0:
            """ Vertex stores seem to start with this line
                So we enter the vertex loading state
            """
            SR = 1 # enter vertex loading state
            # parse a name for our vertex dictionary
            vname = x.replace("static Vtx ","")
            vname = ''.join([c for c in vname if c not in blklist]).strip()
            # add a new entry in our vertex storage
            vertex_dict[vname] = [] 
        if x.find('};') == 0:
            """ If we find a }; in our file most likely we need to leave 
                our current state to exit the file or enter a new state, we also
                need to reset some variables depending on which state we are
                leaving
            """
            # leaving vertex loading state
            if SR:
                # let's pop our last vertex is always empty
                vertex_dict[vname].pop() 
            # leaving model loading state
            if GR: 
                mname = ''
                total_v = 0
                total_t = 0
                voff = -1
            SR = 0
            curT = 0
            GR = 0
            LR = 0 

    for v in model_dict:
        """ Creates the ply files
        """
        mdl = model_dict[v]
        o = open(v + ".ply", 'w')
        o.write("ply\nformat ascii 1.0\n")
        o.write("element vertex %i\n"% len(mdl['v']) )
        for a in ["x","y","z","s","t"]:
            o.write("property float %s\n" % a)
        for a in ["red","green","blue","alpha"]:
            o.write("property uchar %s\n" % a)
        o.write("element face %i\n"% len(mdl['t']) )
        o.write("property list uchar uint vertex_indices\nend_header\n")
        for k in mdl['v']:
            """ Creates the vertex list
            """
            i = mdl['v'][k]
            o.write("%s %s %s %s %s %s %s %s %s\n" % (
                                              xyz_coord(i[0]),
                                              xyz_coord(i[1]),
                                              xyz_coord(i[2]),
                                              to_float(int(i[4]),5),
                                              to_float(int(i[5]),5,True),
                                              i[6],
                                              i[7],
                                              i[8],
                                              i[9]
                                           )
                        )
        for p in mdl['t']:
            """ Creates the faces lists
            """
            o.write("3 %i %i %i\n" % (p[0],p[1],p[2]))

def gfx_to_file(file):
    print("coming soon")
    # Meanwhile ...
    sou_to_file(file)

if __name__ == '__main__':
    main_file = sys.argv[1]
    filename, file_extension = os.path.splitext(main_file)
    if file_extension == '.sou':
        if  'gfx_' in filename:
            gfx_to_file(main_file)
        else:
            sou_to_file(main_file)
    elif file_extension == '.shape':
        sou_to_file(main_file)
    else:
        sou_to_file(main_file)
