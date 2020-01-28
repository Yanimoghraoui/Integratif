# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %% [markdown]
# ## Classe Marmiton (ne pas toucher !)

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


# %%
# install : pip install googletrans
from googletrans import Translator
import csv

# %% [markdown]
# ## Fonctions utiles (ne pas toucher !)

# %%
def Infos_recettes(main_recipe_url):
    detailed_recipe = Marmiton.get(main_recipe_url)  # Get the details of the first returned recipe (most relevant in our case)
     
    return detailed_recipe

def Affiche_Recette(detailed_recipe,nb_personnes):
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
        
def Trouver_Ingredients(liste_rdf,description_marmiton):
    nb_ing = 0
    Liste_ingredients = description_marmiton.lower() # on mets tous les mots en minuscule pour faciliter la comparaison
    for element_liste in liste_rdf: # on parcourt notre liste d'aliments du frigo
        if(Liste_ingredients.find(element_liste)>=0): # si on trouve l'ingrédient du frigo dans la liste d'ingrédients de la base Marmitton
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

    query_url = urllib.parse.urlencode(query_options)
    url = "https://www.marmiton.org/recettes/recherche.aspx?type=all&aqt=" + aliments + "&st=1" + query_url
    Liste_recettes = Marmiton.search_all_recipes(url)
    
    return Liste_recettes

def Trouver_Recettes(liste_rdf,recettes,nb_choix):
    cpt=0
    NB_INGREDIENTS=[]
    Bonnes_recettes=[]
    for r in recettes: # Pour chaque recette
        description = "" # On extrait la description
        for i in r['description']:
            description = description + i
            if(i=='.'):
                break
  
        NB_INGREDIENTS.append(Trouver_Ingredients(liste_rdf,description)) # On stocke tous les nombres d'ingrédients
        
    while(cpt<nb_choix): # On choisit 'nb_choix' recettes 
        idx=NB_INGREDIENTS.index(max(NB_INGREDIENTS))
        Bonnes_recettes.append(recettes[idx])
        cpt=cpt+1
        NB_INGREDIENTS[idx] = 0

    return Bonnes_recettes

def Sacha_Trouve_moi_Recette(liste_rdf_en,nb_personnes,nb_choix,query_options):
    liste_rdf_fr = Traduire_Liste(liste_rdf_en)
    Liste_Recettes = Chercher_Recettes(liste_rdf_fr,query_options)
    Recettes_trouvees = Trouver_Recettes(liste_rdf_fr,Liste_Recettes,nb_choix)

    print("Vous avez %s recettes au choix :" % nb_choix)
    cpt=1
    for recette in Recettes_trouvees:
        print("%s)" %  cpt," %s" % recette["name"])
        cpt=cpt+1

    #choix = input("Votre choix de recette : ")
    choix = 1 #int(choix)-1
    Recette_adaptee = Infos_recettes(Recettes_trouvees[int(choix)]['url'])
    Affiche_Recette(Recette_adaptee,nb_personnes)

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
# ## Recette adaptée au contenu du réfrigérateur
# %% [markdown]
# ### Initialisation de la liste d'aliments (modifiable)

# %%
#liste1=["brick","boeuf","oignon","gousse","curry","gingembre","sauce soja","oeuf","huile d'olive"]      
#liste2=["oignon","tortillas","tomates","boeuf","haricots rouges","poivron vert","feuilles de laitue","Cumin","poivre","sel"]
#liste3=["porc","oignon blanc","carotte","champignons","vermicelles","soja","oeufs","ail","galette de riz","poivre"]

# Fichier contenant les aliments
#fichier = "aliments.csv"

# Définir le nombre de personnes 
#nb_personnes = 3

# Définir le nombre de choix de recettes 
#nb_choix = 3

# Filtrer la recherche
#query_options = {
  #"dt": "platprincipal",      # Type de plat : "entree", "platprincipal", "accompagnement", "amusegueule", "sauce" , "dessert" , "boisson" , "confiserie" (optional)
  #"exp": 2,                   # Coût : 1 -> Cheap, 2 -> Medium, 3 -> Kind of expensive (optional)
  #"dif": 2,                   # Difficulté : 1 -> Very easy, 2 -> Easy, 3 -> Medium, 4 -> Advanced (optional)
  #"prt": 0,                   # Régime : 1 -> Végétarien, 2 -> Sans gluten, 3 -> 'Végan', 4 -> 'Sans lactose' (optional)
  #"ttlt": 15,                 # Temps de cuisson : 15/30/45 minuites (optional)
  #"rct": 1,                   # Type de cuisson : 1 -> four, 3 -> sans cuisson, 4 -> micro-ondes (optional)
#}

# %% [markdown]
# ### Trouver la bonne recette (ne pas toucher !)

# %%
# Extraction de la liste d'aliments (et quantités)
#liste_rdf_en, quantites = Lire_csv(fichier)

# Afficher le contenu du frigo
#Afficher_Contenu_Frigo(liste_rdf_en,quantites)

# Sacha ? Trouve moi une recette !
#Sacha_Trouve_moi_Recette(liste_rdf_en,nb_personnes,nb_choix,query_options)

