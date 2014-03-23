#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Tues. January 14 2014

@author: - E. Olivi
"""

import sys
import numpy as np
import openmeeg as om
from om_basics import om_load_headmodel # openmeeg basics
from om_display import om_display_vtp # visualiation with VTK
from os import path as op

# recompute or load matrices ?
recompute = True
recompute_HMi = False

###############################################################################
# Load data

def main(argv):

    filename = 'leadfields/HDTDCS_' + argv + '.vtp'
    filename_HMi = op.join('tmp', argv + '_HMi.mat')

    if recompute:
        model = om_load_headmodel(argv)
        if recompute_HMi or not op.exists(filename_HMi): 
            hm = om.HeadMat(model['geometry'])
            hm.invert()
            hm.save(str(filename_HMi))
        else:
            print "Loading " + str(filename_HMi)
            hm = om.SymMatrix(str(filename_HMi))

        sm = om.EITSourceMat(model['geometry'], model['tdcssources'])
        # set here the input currents (actually a current density [I/L])
        activation = om.fromarray(np.array([[-4., 1.],[1., -4.],[1., 1.],[1., 1.],[1., 1.]])) # each column must have a zero mean
        # now apply the currents and get the result
        X = hm*(sm*activation)
        # concatenate X with input currents (to see the what was injected)
        Xt = np.append(om.asarray(X), np.zeros((model['geometry'].size()-X.nlin(),X.ncol())),0)
        currents = om.asarray(activation)
        for s in range(model['tdcssources'].getNumberOfSensors()):
            # get the triangles supporting this sensor
            tris = model['tdcssources'].getInjectionTriangles(s)
            for it in tris:
                Xt[it.getindex(),:] = currents[s,:]*model['tdcssources'].getWeights()(s)

        X = om.fromarray(Xt)
        model['geometry'].write_vtp(str(filename), X)

    om_display_vtp(filename)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        main("canonical")
    else:
        main(sys.argv[1])
