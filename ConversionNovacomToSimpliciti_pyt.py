import arcpy
import datetime
import pandas as pd
from tkinter import filedialog, simpledialog
import os
import math
import numpy as np
from numpy import (array, dot, arccos, clip)
from numpy.linalg import norm

## PARAMETRES ##

# Distance mini entre 2 points pour prise en compte
distMin = 100
#Angle mini en degrés entre 3 points pour prise en compte
angleMin = 10

## FONCTIONS ##

## A. Calcul de l'angle ##

def get_point_direction(x,y,x0,y0):

    num = x - x0
    den = np.sqrt( ( x - x0 )**2 + ( y - y0 )**2 )

    theta = np.arccos( num / den )

    if not y - y0 >= 0: theta = 2 * np.pi - theta

    theta = np.rad2deg(theta)

    return theta

def get_vector_angle(x0,y0,x1,y1,x2,y2):
    
    x01 = x1 - x0
    y01 = y1 - y0
    x12 = x2 - x1
    y12 = y2 - y1
    u=array([x01,y01])
    v=array([x12,y12])
    c = dot(u,v)/norm(u)/norm(v)
    angle = np.rad2deg(arccos(clip(c, -1, 1)))
                      
    return angle

def get_distance(x,y,x0,y0):
    
    R = 6371000
    distX = (math.radians(y) - math.radians(y0)) * math.cos(0.5*(math.radians(x) + math.radians(x0)))
    distY = math.radians(x) - math.radians(x0)
    distXY = R * math.sqrt( distX*distX + distY*distY )
    
    return distXY


## 0 ## Créaation de la dataframe

FichierSource = filedialog.askopenfilename(title='Sélection du fichier .SHP')
ID_Tournee = simpledialog.askstring("Nom de la tournée", "Ecrire le nom de la tournée :")
RepertoireSortie = os.path.dirname(FichierSource)

arcpy.ImportToolbox(r"E:\arcgispro\Resources\ArcToolbox\toolboxes\Data Management Tools.tbx")
arcpy.ImportToolbox(r"E:\arcgispro\Resources\ArcToolbox\toolboxes\Conversion Tools.tbx")

data = pd.DataFrame(columns=['X','Y','index'])


## 1 ## Déclaration du chemin du fichier en sortie

ajd1 = datetime.datetime.today()
ajd2 = datetime.datetime.strftime(ajd1, '%Y%m%d_%H%M%S_')

CheminFichierSortie = RepertoireSortie + "\\" + ajd2 + ID_Tournee + ".csv"


## 2 ## Transformation des lignes en points + enregistrement dans une dataframe

polylignept = [] # Liste des paires latitude/longitude et de l'ordre
i=0
for row in arcpy.da.SearchCursor(FichierSource, ["SHAPE@", "CLE", "TYPECOL_00"]): # Boucle sur les entités dans le fichier source (le curseur parcours les entités tronçon par tronçon)
        shapein = row[0] # Géométrie du tronçon
        for part in shapein:
                for pnt in part:
                        i=i+1
                        x = float(pnt.X)
                        y = float(pnt.Y)
                        nv_ligne = {'X':x,'Y':y,'index':i, 'dist':0}
                        data = data.append(nv_ligne, ignore_index=True)


## 3 ## Nettoyage des points superposés

for i in range(len(data)):
    if i > 0:
        data.loc[i,"dist"] = get_distance(data.loc[i,'X'],data.loc[i,'Y'],data.loc[i-1,'X'],data.loc[i-1,'Y'])
    else:
        data.loc[i,"dist"] = 0

indexNames = data[data['dist'] < 5 ].index.drop(0)
data = data.drop(indexNames)
data = data.reset_index(drop=True)


## 4 ## Nettoyage à partir de l'angle

for i in range(len(data)):
    if i > 0 and i < len(data) - 1:
        data.loc[i,"angle"] = get_vector_angle(data.loc[i-1,"X"],data.loc[i-1,"Y"],data.loc[i,"X"],data.loc[i,"Y"],data.loc[i+1,"X"],data.loc[i+1,"Y"])
    else:
        data.loc[i,"angle"] = 0

indexNames = data[data['angle'] < angleMin ].index.drop(0)
data = data.drop(indexNames)
data = data.reset_index(drop=True)

## 5 ## Double nettoyage des points proches (< distMin)

for i in range(len(data)):
    if i > 0 and i < len(data) - 1:
        data.loc[i,"dist"] = get_distance(data.loc[i,'X'],data.loc[i,'Y'],data.loc[i-1,'X'],data.loc[i-1,'Y'])
        data.loc[i,"angle"] = get_vector_angle(data.loc[i-1,"X"],data.loc[i-1,"Y"],data.loc[i,"X"],data.loc[i,"Y"],data.loc[i+1,"X"],data.loc[i+1,"Y"])
    else:
        data.loc[i,"dist"] = 0
        data.loc[i,"angle"] = 0

indexNames = data[(data['dist'] < distMin) & (data['angle'] < 45)].index.drop(0)
data = data.drop(indexNames)
data = data.reset_index(drop=True)

for i in range(len(data)):
    if i > 0 and i < len(data) - 1:
        data.loc[i,"dist"] = get_distance(data.loc[i,'X'],data.loc[i,'Y'],data.loc[i-1,'X'],data.loc[i-1,'Y'])
        data.loc[i,"angle"] = get_vector_angle(data.loc[i-1,"X"],data.loc[i-1,"Y"],data.loc[i,"X"],data.loc[i,"Y"],data.loc[i+1,"X"],data.loc[i+1,"Y"])
    else:
        data.loc[i,"dist"] = 0
        data.loc[i,"angle"] = 0

indexNames = data[data['dist'] < 30].index.drop(0)
data = data.drop(indexNames)
data = data.reset_index(drop=True)


## 6 ## Calcul des attributs géométriques

for i in range(len(data)):
    if i > 0 and i < len(data) - 1:
        data.loc[i,"dist"] = get_distance(data.loc[i,'X'],data.loc[i,'Y'],data.loc[i-1,'X'],data.loc[i-1,'Y'])
        data.loc[i,"angle"] = get_vector_angle(data.loc[i-1,"X"],data.loc[i-1,"Y"],data.loc[i,"X"],data.loc[i,"Y"],data.loc[i+1,"X"],data.loc[i+1,"Y"])
    else:
        data.loc[i,"dist"] = 0
        data.loc[i,"angle"] = 0


## 7 ## Export de la dataframe vers CSV

data = data.drop(['dist','angle'], axis=1)
data.loc[:,'index'] = data.index
data = data.astype({"X": float, "Y": float, 'index': int})
data.to_csv(CheminFichierSortie, index=False, sep=';')