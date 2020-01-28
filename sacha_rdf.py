#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
	Ce programme lance une analyse du réseau YOLO v3sur l'image à l'emplacement image_path.
	Ensuite le programme enregistre dans un fichier csv la liste du contenu d'éléments dans l'image.
		image_path : chemin menan à l'image nécessitant une analyse
		th : seuil de détection après les résultats fournis par YOLOv3
	
"""
import sys, os
sys.path.append(os.path.join(os.getcwd(),'python/'))

import darknet as dn
import pdb
image_path = b"data/fridge.jpg"
th = .32
# dn.set_gpu(0) # Permet d'utiliser la carte graphique pour accélerer les calculs
# Chargement des paramètres du réseau YOLO préentrainé.
net = dn.load_net(b"./cfg/yolov3.cfg", b"./yolov3.weights",0)
meta = dn.load_meta(b"./cfg/coco.data")
# On fait passer notre image dans le réseau
r = dn.detect(net, meta, image_path,th,th)# On fixe le seuil de détection à 30 %

import numpy as np
aliments={}
for i in range (len(r)):
    if r[i][0].decode("utf-8").replace("'","") in aliments:
        aliments[r[i][0].decode("utf-8").replace("'","")]+=1
    else:
        aliments[r[i][0].decode("utf-8").replace("'","")]=1

from pandas import DataFrame
import pandas as pd

# On détaille la liste de course présente dans le réfrigirateur dans un fichier appelé aliments.csv
with open('aliments.csv', 'w') as f:
    for key in aliments.keys():
        f.write("%s,%s\n"%(key,aliments[key]))

d=pd.read_csv('./aliments.csv')  # doctest: +SKIP
print("\n")
print(d)




