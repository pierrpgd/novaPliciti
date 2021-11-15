import arcpy
import datetime
import pandas as pd
from tkinter import filedialog, simpledialog
import os
import math

# FichierSource = arcpy.GetParameterAsText(0)
# ID_Tournee = arcpy.GetParameterAsText(1)
# RepertoireSortie = arcpy.GetParameterAsText(2)

FichierSource = filedialog.askopenfilename(title='Sélection du fichier .SHP')
ID_Tournee = simpledialog.askstring("Nom de la tournée", "Ecrire le nom de la tournée :")
RepertoireSortie = os.path.dirname(FichierSource)

# FichierSource = r"C:/Users/pagaudp.PAPRECPROD/Desktop/novacom waziers/4738116_PL.shp"
# ID_Tournee = "TEST"
# RepertoireSortie = r"C:/Users/pagaudp.PAPRECPROD/Desktop/novacom waziers"

arcpy.ImportToolbox(r"E:\arcgispro\Resources\ArcToolbox\toolboxes\Data Management Tools.tbx")
arcpy.ImportToolbox(r"E:\arcgispro\Resources\ArcToolbox\toolboxes\Conversion Tools.tbx")

## 0 ## Créaation de la dataframe

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

## 3 ## Nettoyage des points

R = 6371
for i in range(len(data)):
    if i > 0:
        distX = (math.radians(data.loc[i,'Y']) - math.radians(data.loc[i - 1,'Y'])) * math.cos(0.5*(math.radians(data.loc[i,'X']) + math.radians(data.loc[i - 1,'X'])))
        distY = math.radians(data.loc[i,'X']) - math.radians(data.loc[i - 1,'X'])
        distXY = R * math.sqrt( distX*distX + distY*distY )
        data.loc[i,"dist"] = distXY
    else:
        data.loc[i,"dist"] = 0

## 4 ## Export de la dataframe vers CSV

data = data.astype({"X": float, "Y": float, 'index': int})
data.to_csv(CheminFichierSortie, index=False, sep=';')
