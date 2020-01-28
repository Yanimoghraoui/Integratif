from flask import Flask
from flask import send_file, request, Response, render_template
from sacha_all2 import *
import os
#import json
import jsonpickle
import base64
import numpy as np
import cv2

#from sacha_audio import *

app = Flask(__name__)

@app.route('/')
def hello_world():
	return 'Hello, World!'

@app.route("/description")
def description():
	return render_template('Frigo.html')
	

@app.route("/upload")
def test():
	r = request
    # convert string of image data to uint8
	nparr = np.fromstring(r.data, np.uint8)
    # decode image
	img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    # do some fancy processing here....

    # build a response dict to send back to client
	response = {'message': 'image received. size={}x{}'.format(img.shape[1], img.shape[0])
                }
    # encode response using jsonpickle
	response_pickled = jsonpickle.encode(response)

	fh = open("imageToSave.jpg", "wb")
	fh.write(img)
	fh.close()
	#img.save(os.path.join('/home/Integratif/Serveur', img))

	return Response(response=response_pickled, status=200, mimetype="application/json")

@app.route('/image')
def get_image():
	#filename = 'photo.jpg'
	#return send_file(filename, mimetype='image/jpg')
	photo = "<html><body><h2>Image du frigo</h2> <img src='photo.jpg' alt='Image' width='500' height='333'></body></html>"
	return photo

@app.route('/ingredient')
def disp_ingredient():
	liste_ingredient = ["patate","carotte"]

	code = ""
	code += '<html><head>  <title>Ma première page avec du style</title> </head>'
	code += '<body>'
	code += 'Bonjour Monsieur vieux voici votre frigo ' + " ".join(liste_ingredient) + '</body></html>'
	return code

@app.route('/recette')
def disp_recette():
	# %% [markdown]
	# # Recette adaptée au contenu du réfrigérateur
	# %% [markdown]
	# ## Initialisation de la liste d'aliments
	# %% [markdown]
	# ### <font color=green> Modifiable </font>
	
	# %%
	#liste1=["brick","boeuf","oignon","gousse","curry","gingembre","sauce soja","oeuf","huile d'olive"]      
	#liste2=["oignon","tortillas","tomates","boeuf","haricots rouges","poivron vert","feuilles de laitue","Cumin","poivre","sel"]
	#liste3=["porc","oignon blanc","carotte","champignons","vermicelles","soja","oeufs","ail","galette de riz","poivre"]
	
	# Fichier contenant les aliments
	fichier = "aliments.csv"
	
	# Définir le nombre de choix de recettes 
	nb_choix = 3         
	
	# %% [markdown]
	# ###  <font color=red> Ne pas toucher ! </font>
	
	# %%
	#Type de plat
	type_plat = ["l'entrée","le plat principal","le dessert"]
	dt_set = ["entree","platprincipal","dessert"] 
	
	# Initialisation par défaut
	query_options = {
	"dt": -1,     # Type de plat : "entree", "platprincipal", "accompagnement", "amusegueule", "sauce" , "dessert" , "boisson" , "confiserie" (optional)
	"dif": -1,    # Difficulté : 1 -> Very easy, 2 -> Easy, 3 -> Medium, 4 -> Advanced (optional)
	"exp": -1,    # Coût : 1 -> Cheap, 2 -> Medium, 3 -> Kind of expensive (optional)
	"prt": -1,    # Régime : 1 -> Végétarien, 2 -> Sans gluten, 3 -> 'Végan', 4 -> 'Sans lactose' (optional)
	"rct": -1,    # Type de cuisson : 1 -> four, 3 -> sans cuisson, 4 -> micro-ondes (optional)
	"ttlt": -1,   # Temps de cuisson : 15/30/45 minuites (optional)
	}
	
	# %% [markdown]
	# ###  <font color=green> Filtrer la recherche (modifiable) </font>
	
	# %%
	param_defaut = 0
	# Cas 1 : 
	# Si on veut la liste des recettes pour les 3 types de plat : param_defaut = 1.
	# ----> Dans ce cas, on ne peut pas choisir un type de plat en particulier
	
	# Cas 2 :
	# Si on veut la liste des recettes pour n'importe quel type de plat : param_defaut = 0. 
	# ----> Dans ce cas, on peut choisir un type de plat particulier (choix obligatoire dans le cas 2) :
	# query_options["dt"] = "boisson" # Type de plat : "entree", "platprincipal", "accompagnement", "amusegueule", "sauce" , "dessert" , "boisson" , "confiserie" (optional)
	
	# Remarque : dans les 2 cas, on peut rajouter des critères (régime, coût, difficulté ...) :
	# -----> Pour modifier/ajouter des préférences (enlever les commentaires si nécessaire) : 
	#query_options["dif"] = ... # Difficulté : 1 -> Very easy, 2 -> Easy, 3 -> Medium, 4 -> Advanced (optional)
	#query_options["exp"] = ... # Coût : 1 -> Cheap, 2 -> Medium, 3 -> Kind of expensive (optional)
	#query_options["prt"] = ... # Régime : 1 -> Végétarien, 2 -> Sans gluten, 3 -> 'Végan', 4 -> 'Sans lactose' (optional)
	#query_options["rct"] = ... # Type de cuisson : 1 -> four, 3 -> sans cuisson, 4 -> micro-ondes (optional)
	#query_options["ttlt"] = ... # Temps de cuisson : 15/30/45 minuites (optional)     
	
	# %% [markdown]
	# ##   <font color=red> Sacha ? Trouve moi une recette ! (ne pas toucher !) </font>
	
	# %%
	#start_time = time.time()
	Recettes_par_type,frigo,recette_texte = Sacha_Trouve_Moi_Recettes(fichier,nb_choix,type_plat,dt_set,param_defaut,query_options)
	#print("\nTemps d execution : %s secondes ---" % (time.time() - start_time))
	
	# %% [markdown]
	# ##   Sacha ? Je veux une recette ! (ne pas toucher !)
	# %% [markdown]
	# ###   <font color=green> Modifiable </font>
	
	# %%
	# Choix du type de plat (1-> entrée | 2-> plat principal | 3-> dessert)
	choix_type_plat = 1
	
	# Choix de la recette (1,2,3,...,nb_choix)
	choix_recette = 1  
	
	# %% [markdown]
	# ###   <font color=red> Ne pas toucher ! </font>
	
	
	return recette_texte





