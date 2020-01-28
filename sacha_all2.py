# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %% [markdown]
# # <font color=red> Classe Marmiton (ne pas toucher !) </font>

# %%
from bs4 import BeautifulSoup

import urllib.parse
import urllib.request
import re

class Marmiton(object):
    
	def search_all_recipes(base_url):
		url = base_url
        
		html_content = urllib.request.urlopen(url).read()
		soup = BeautifulSoup(html_content, 'html.parser')

		search_data = []
                
		articles = soup.findAll("div", {"class": "recipe-card"})

		iterarticles = iter(articles)
		for article in iterarticles:
			data = {}
			try:
				data["name"] = article.find("h4", {"class": "recipe-card__title"}).get_text().strip(' \t\n\r')
				data["description"] = article.find("div", {"class": "recipe-card__description"}).get_text().strip(' \t\n\r')
				data["url"] = article.find("a", {"class": "recipe-card-link"})['href']
				data["rate"] = article.find("span", {"class": "recipe-card__rating__value"}).text.strip(' \t\n\r')
				try:
					data["image"] = article.find('img')['src']
				except Exception as e1:
					pass
			except Exception as e2:
				pass
			if data:
				search_data.append(data)

		return search_data

	@staticmethod
	def __clean_text(element):
		return element.text.replace("\n", "").strip()

	@staticmethod
	def get(uri):
		"""
		'url' from 'search' method.
		 ex. "/recettes/recette_wraps-de-poulet-et-sauce-au-curry_337319.aspx"
		"""
		data = {}

		base_url = "http://www.marmiton.org/"
		url = base_url + uri

		html_content = urllib.request.urlopen(url).read()
		soup = BeautifulSoup(html_content, 'html.parser')

		main_data = soup.find("div", {"class": "m_content_recette_main"})
		try:
			name = soup.find("h1", {"class", "main-title "}).get_text().strip(' \t\n\r')
		except:
			name = soup.find("h1", {"class", "main-title"}).get_text().strip(' \t\n\r')

		ingredients = [item.text.replace("\n", "").strip() for item in soup.find_all("li", {"class": "recipe-ingredients__list__item"})]

		try:
			tags = list(set([item.text.replace("\n", "").strip() for item in soup.find('ul', {"class": "mrtn-tags-list"}).find_all('li', {"class": "mrtn-tag"})]))
		except:
			tags = []

		recipe_elements = [
			{"name": "author", "query": soup.find('span', {"class": "recipe-author__name"}) },
			{"name": "rate", "query": soup.find("span", {"class": "recipe-reviews-list__review__head__infos__rating__value"}) },
			{"name": "difficulty", "query": soup.find("div", {"class": "recipe-infos__level"}) },
			{"name": "budget", "query": soup.find("div", {"class": "recipe-infos__budget"}) },
			{"name": "prep_time", "query": soup.find("span", {"class": "recipe-infos__timmings__value"}) },
			{"name": "total_time", "query": soup.find("span", {"class": "title-2 recipe-infos__total-time__value"}) },
			{"name": "people_quantity", "query": soup.find("span", {"class": "title-2 recipe-infos__quantity__value"}) },
			{"name": "author_tip", "query": soup.find("div", {"class": "recipe-chief-tip mrtn-recipe-bloc "}).find("p", {"class": "mrtn-recipe-bloc__content"}) if soup.find("div", {"class": "recipe-chief-tip mrtn-recipe-bloc "}) else "" },
		]
		for recipe_element in recipe_elements:
			try:
				data[recipe_element['name']] = Marmiton.__clean_text(recipe_element['query'])
			except:
				data[recipe_element['name']] = ""

		try:
			cook_time = Marmiton.__clean_text(soup.find("div", {"class": "recipe-infos__timmings__cooking"}).find("span"))
		except:
			cook_time = "0"

		try:
			nb_comments = Marmiton.__clean_text(soup.find("span", {"class": "recipe-infos-users__value mrtn-hide-on-print"})).split(" ")[0]
		except:
			nb_comments = ""

		steps = []
		soup_steps = soup.find_all("li", {"class": "recipe-preparation__list__item"})
		for soup_step in soup_steps:
			soup_step.find("h3").decompose()
			steps.append(Marmiton.__clean_text(soup_step))

		image = soup.find("img", {"id": "af-diapo-desktop-0_img"})['src'] if soup.find("img", {"id": "af-diapo-desktop-0_img"}) else ""

		data.update({
			"ingredients": ingredients,
			"steps": steps,
			"name": name,
			"tags": tags,
			"image": image if image else "",
			"nb_comments": nb_comments,
			"cook_time": cook_time
		})

		return data

# %% [markdown]
# # <font color=red> Fonctions utiles (ne pas toucher !) </font>

# %%
# install : pip install googletrans
from googletrans import Translator
import csv
import time


# %%
def Infos_recettes(main_recipe_url):
    detailed_recipe = Marmiton.get(main_recipe_url)  # Get the details of the first returned recipe (most relevant in our case)
    
    return detailed_recipe

def Affiche_Recette(detailed_recipe):
    Recette = "<html><head>Recette</head><body>"
    Recette = "<br>##### " + detailed_recipe['name']
    Recette = Recette + "<br>##### Recette pour " + detailed_recipe['people_quantity'] + " personne(s)." + "Adapter les proportions selon le nombre de personnes"
    Recette = Recette + "<br>##### Temps de cuisson : " 
    if(detailed_recipe['cook_time']):
        Recette = Recette + detailed_recipe['cook_time'] 
    else:
        Recette = Recette + "N/A"
    
    Recette = Recette + " / Temps de préparation : " + detailed_recipe['prep_time'] + " / Temps total : " + detailed_recipe['total_time'] + "."
    Recette = Recette + "<br>##### Difficulté : '" + detailed_recipe['difficulty'] + "'"
    Recette = Recette + "<br>##### Budget : '" + detailed_recipe['budget'] + "'"
    Recette = Recette + "<br>##### Ingrédients :"
    for ingredient in detailed_recipe['ingredients']:
        ingredient_modif = ""
        if(len(re.findall('\d+', ingredient))!=0):
            idx = ingredient.index(re.findall('\d+', ingredient)[-1]) + len(re.findall('\d+', ingredient)[-1])
            ingredient_modif = ingredient[:idx] + " " + ingredient[idx:]
            Recette = Recette + "<br>- " + ingredient_modif           
        else: 
            Recette = Recette + "<br>- " + ingredient
            
    Recette = Recette + "<br><br>"
    Recette = Recette + "<br>##### Etapes de la recette :"
    num_etape=1
    for step in detailed_recipe['steps']:  # List of cooking steps
        Recette = Recette + "<br>" + str(num_etape) + ") " + step
        num_etape=num_etape+1

    if detailed_recipe['author_tip']:
        Recette = Recette + "<br>Astuces :<br>" + detailed_recipe['author_tip']
    
    Recette = Recette + "</body></html>"
    return Recette
        
    """
    # Display result :
    print("\n##### %s" % detailed_recipe['name'])  # Name of the recipe
    print("##### Recette pour %s personne(s)." % detailed_recipe['people_quantity'], "Adapter les proportions selon le nombre de personnes")
    #print("Pour %s personne(s)," % nb_personnes, "multiplier les proportions par %s" %nb_personnes, "/ %s." %detailed_recipe['people_quantity'])
    #print("Noté %s/5 par %s personnes." % (detailed_recipe['rate'], detailed_recipe['nb_comments']))
    print("##### Temps de cuisson : %s / Temps de préparation : %s / Temps total : %s." % (detailed_recipe['cook_time'] if detailed_recipe['cook_time'] else 'N/A',detailed_recipe['prep_time'], detailed_recipe['total_time']))
    #print("##### Tags : %s" % (", ".join(detailed_recipe['tags'])))
    print("##### Difficulté : '%s'" % detailed_recipe['difficulty'])
    print("##### Budget : '%s'" % detailed_recipe['budget'])
    print("##### Ingrédients :")   
    for ingredient in detailed_recipe['ingredients']:
        ingredient_modif = ""
        if(len(re.findall('\d+', ingredient))!=0):
            idx = ingredient.index(re.findall('\d+', ingredient)[-1]) + len(re.findall('\d+', ingredient)[-1])
            ingredient_modif = ingredient[:idx] + " " + ingredient[idx:]
            print("- %s" % ingredient_modif)            
        else: 
            print("- %s" % ingredient)
                

    print("")
    print("##### Etapes de la recette :")  
    num_etape=1
    for step in detailed_recipe['steps']:  # List of cooking steps
        print("%d)" % num_etape, "%s" % step)
        num_etape=num_etape+1

    if detailed_recipe['author_tip']:
        print("\nAstuces :\n%s" % detailed_recipe['author_tip'])
    """   
def Trouver_Ingredients(liste_rdf,description):
    nb_ing = 0
    
    Liste_ingredients = []
    aliment=""
    for c in description: 
        if(c!=','):
            aliment = aliment + c
        else:
            Liste_ingredients.append(aliment.lower()) # on mets tous les mots en minuscule pour faciliter la comparaison
            aliment=""
    
    for element_liste in liste_rdf: # on parcourt notre liste d'aliments du frigo
        for element_ing in Liste_ingredients:
            if(element_liste in element_ing): 
                if(len(re.findall('\d+', element_ing))!=0):
                    idx = element_ing.index(re.findall('\d+', element_ing)[-1]) + len(re.findall('\d+', element_ing)[-1])
                    if(len(element_ing[idx:])-len(element_liste)<=2):
                        nb_ing=nb_ing+1 # incrémentation d'un compteur
                else: 
                    if(len(element_ing)-len(element_liste)<=2):
                        nb_ing=nb_ing+1 # incrémentation d'un compteur                       
    return nb_ing

def Chercher_Recettes(liste_rdf,query_options):
    aliments=""
    for i in range(len(liste_rdf)-1):
        aliment = liste_rdf[i]
        aliment = aliment.replace(" ","-")
        aliment = aliment.replace("'","-")
        aliments = aliments + aliment + "-" 

    aliment = liste_rdf[len(liste_rdf)-1]
    aliment = aliment.replace(" ","-")
    aliment = aliment.replace("'","-")
    aliments= aliments + aliment

    # Définition de l'URL
    query_url = ""
    for elt in query_options:
        if(query_options[elt] != -1):
            query_url = query_url + "&" + elt + "=" + query_options[elt]

    url = "https://www.marmiton.org/recettes/recherche.aspx?type=all&aqt=" + aliments + "&st=1" + query_url
    
    # Recherche des recettes correspondant aux critères
    Liste_recettes = Marmiton.search_all_recipes(url)
    
    return Liste_recettes

def Trouver_Recettes(liste_rdf,recettes,nb_choix):
    cpt=0
    NB_INGREDIENTS=[]
    Bonnes_recettes=[]

    for r in recettes: # Pour chaque recette
        description = "" # On extrait la description
        ok=0
        for i in r['description']:
            if(i==':'):
                ok=1
            if(ok):
                description = description + i
                if(i=='.'):
                    break
        
        NB_INGREDIENTS.append(Trouver_Ingredients(liste_rdf,description[1:])) # On stocke tous les nombres d'ingrédients
        
    while(cpt<nb_choix): # On choisit 'nb_choix' recettes 
        idx=NB_INGREDIENTS.index(max(NB_INGREDIENTS))
        Bonnes_recettes.append(recettes[idx])
        cpt=cpt+1
        NB_INGREDIENTS[idx] = 0

    return Bonnes_recettes

# Entrées : 
# - Liste des recettes (x3 entrée / x3 plat principal / x3 dessert)
# - type_plat : "l'entrée", "le plat principal", "le dessert"
# - num_recette : 1,2,3,...,nb_choix
def Je_veux_cette_recette1(Liste_recettes,type_plat,num_recette):
    Recette_voulue = Infos_recettes(Liste_recettes[type_plat][num_recette-1]['url'])
    Affiche_Recette(Recette_voulue)
    
    return Recette_voulue

def Je_veux_cette_recette2(Liste_recettes,num_recette):
    Recette_voulue = Infos_recettes(Liste_recettes[num_recette-1]['url'])
    Affiche_Recette(Recette_voulue)
    
    return Recette_voulue

def Sacha_Trouve_Moi_Recettes(fichier,nb_choix,type_plat,dt_set,param_defaut = 1, query_options={}):
    # Extraction de la liste d'aliments (et quantités)
    liste_rdf_en, quantites = Lire_csv(fichier)

    # Afficher le contenu du frigo
    Afficher_Contenu_Frigo(liste_rdf_en,quantites)
    
    # Traduire la liste en français
    liste_rdf_fr = Traduire_Liste(liste_rdf_en)
    
    if(not(liste_rdf_fr)):
        return "Le réfrigérateur est vide !"
        
    Recettes_par_type = {}  

    if(param_defaut==1):
        # Trouver les recettes par type de plat
        for (elt_type_plat,dt) in zip(type_plat,dt_set):
            query_options["dt"] = dt
            Liste_Recettes = Chercher_Recettes(liste_rdf_fr,query_options)
            Recettes_trouvees = Trouver_Recettes(liste_rdf_fr,Liste_Recettes,nb_choix)
            Recettes_par_type[elt_type_plat] = Recettes_trouvees
            print("Vous avez %s recettes au choix pour %s :" % (nb_choix,elt_type_plat))
            cpt=1
            for recette in Recettes_trouvees:
                print("%s)" %  cpt," %s" % recette["name"])
                cpt=cpt+1

        """
        choix_type_plat = input("Votre choix du type de plat : ")
        choix_type_plat = int(choix_type_plat)
        choix_recette = input("Votre choix de recette : ")
        choix_recette = int(choix_recette)-1

        if(choix_type_plat==1):
            Recette_adaptee = Infos_recettes(Recettes_par_type[type_plat[0]][int(choix_recette)]['url'])
        elif(choix_type_plat==2):
            Recette_adaptee = Infos_recettes(Recettes_par_type[type_plat[1]][int(choix_recette)]['url'])
        elif(choix_type_plat==3):
            Recette_adaptee = Infos_recettes(Recettes_par_type[type_plat[2]][int(choix_recette)]['url'])
        else:
            return "Je n'ai pas compris !"
        """
        Recette_adaptee = Infos_recettes(Recettes_par_type[type_plat[0]][0]['url'])
        
        Recette_adaptee_texte = Affiche_Recette(Recette_adaptee)
        
        #print(Recette_adaptee_texte)
        
        return Recettes_par_type,liste_rdf_fr,Recette_adaptee_texte
    
    elif(param_defaut==0):
        Liste_Recettes = Chercher_Recettes(liste_rdf_fr,query_options)
        Recettes_trouvees = Trouver_Recettes(liste_rdf_fr,Liste_Recettes,nb_choix)
        print("Vous avez %s recettes au choix :" % nb_choix)
        cpt=1
        for recette in Recettes_trouvees:
            print("%s)" %  cpt," %s" % recette["name"])
            cpt=cpt+1
            
        #choix_recette = input("Votre choix de recette : ")
        choix_recette =1# int(choix_recette)-1
        Recette_adaptee = Infos_recettes(Recettes_trouvees[int(choix_recette)]['url'])
        Recette_adaptee_texte = Affiche_Recette(Recette_adaptee)
        #print(Recette_adaptee_texte)
        Recettes_par_type = Recettes_trouvees
        return Recettes_par_type,liste_rdf_fr,Recette_adaptee_texte
    
    else:
        return "Erreur !"
    
def Afficher_Contenu_Frigo(liste_rdf_en,quantites):
    liste_rdf_fr = Traduire_Liste(liste_rdf_en)
    
    # Tous les aliments en minuscule
    l_min = []
    for aliment in liste_rdf_fr:
        l_min.append(aliment.lower())
    
    # Singulier / Pluriel
    l2 = []
    for (aliment,quantite) in zip(l_min,quantites):
        if(int(quantite)>1):
            if(aliment[-1] != 's' and aliment[-1] != 'x'):
                aliment_modif = aliment + 's'
                l2.append(aliment_modif)
        else:
            l2.append(aliment)
            
    print("Votre réfrigérateur contient : ")
    for aliment,quantite in zip(l2,quantites):
        print("- %s %s" % (quantite,aliment))
      
    print("")

def Trouver_Ingredients_Manquants_Recette(liste_rdf_fr,ingredients_recette):
    for aliment in liste_rdf_fr:
        cpt=0
        for ingredient in ingredients_recette:
            if(aliment in ingredient.lower()):
                if(len(re.findall('\d+', ingredient))!=0):
                    idx = ingredient.index(re.findall('\d+', ingredient)[-1]) + len(re.findall('\d+', ingredient)[-1])
                    if(len(ingredient[idx:])-len(aliment)<=2):
                        del ingredients_recette[cpt]
                        break
                else: 
                    if(len(ingredient)-len(aliment)<=2):
                        del ingredients_recette[cpt]
                        break
            cpt =cpt + 1        
    return ingredients_recette
                
    
def Traduire_Liste(liste_rdf_en):
    t = Translator()
    liste_rdf_fr=[]
    for word in liste_rdf_en:
        mot = t.translate(word,dest='fr')
        liste_rdf_fr.append(mot.text)
        
    return liste_rdf_fr

def Lire_csv(fichier):
    cr = csv.reader(open(fichier,"rt"))
    liste_rdf_en=[]
    quantites=[]
    for row in cr:
        liste_rdf_en.append(row[0])
        quantites.append(row[1])

    return liste_rdf_en,quantites

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
#Recettes_par_type,frigo,recette_texte = Sacha_Trouve_Moi_Recettes(fichier,nb_choix,type_plat,dt_set,param_defaut,query_options)
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

"""
# %%
# Rappel : type_plat = ["l'entrée","le plat principal","le dessert"]
if(param_defaut==1):
    Recette_voulue = Je_veux_cette_recette1(Recettes_par_type,type_plat[choix_type_plat-1],choix_recette)
elif(param_defaut==0):
    Recette_voulue = Je_veux_cette_recette2(Recettes_par_type,choix_recette)   
"""
# %% [markdown]
# ###  <font color=red> Les ingrédients manquants pour la recette (ne pas toucher !) </font>

# %%
#Ingredients_Manquants = Trouver_Ingredients_Manquants_Recette(frigo, Recette_voulue['ingredients'])
#Ingredients_Manquants




