# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import speech_recognition as sr
import pandas as pd
import csv
from bs4 import BeautifulSoup
import urllib.parse
import urllib.request
import re
from gtts import gTTS
import vlc
import time


def recognize_system(audio_stt):                        ### How can Sacha help ? 
    
    #### Liste des mots auquels on devrait reconnaitre
    list_command=['comment ça va','aide','recette','quoi dans mon frigo','liste des courses','ça va merci', 'merci Sacha']

    cpt=0
    for i in list_command:    ##### Parcourir tous les mots
        if i in audio_stt:    ##### Est ce que le mot figure dans le text from speech to text ?
            
            if i=='recette':
                response="Voyons voir ce que vous pouvez mijoter avec le contenu de votre frigo:"
                tts_play(response)
                time.sleep(2)
                
                ################# Tu peux mettre ta fonction de recettes ici #######################
                ### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
                #################################################################################

                return "Que puis-je faire pour vous maintenant ?"
                

            elif i== 'ça va merci' :
                return "Que puis-je faire pour vous ?"
                
            elif i== 'comment ça va' :
                return "ça va merci et vous ?"

            elif i== 'quoi dans mon frigo' :
                response = "Voici le contenu de votre frigo:"
                tts_play(response)
                time.sleep(3)
                
                ################# Tu peux mettre ta fonction de frigo ici #######################
                ### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###
                #################################################################################
                
                return "Que puis-je faire pour vous maintenant ?"


            elif i== 'liste des courses' :
                return "voici votre liste de courses"

            elif i== 'merci Sacha' :
                return "A votre service :D Bye bye"

            else:
                return "Que puis-je faire pour vous ?"
        cpt+=1
        if cpt==len(list_command):
            return "Désolé je n'ai pas compris. Pouvez vous répéter S'il vous plaît ?"

def micro_activation():
    response=''

    while response != 'A votre service :D Bye bye':   ###### Tant qu'on n'a pas dit "Merci Sacha"

        error=0
        r=sr.Recognizer()
        with sr.Microphone() as source:
            audio=r.adjust_for_ambient_noise(source)
            print("\n#### listening ####")
            audio=r.record(source, duration=3)
            print("#### end of listening ####")
 
        try:
            response=recognize_system(r.recognize_google(audio, language="fr-FR"))    #### reconnaitre ce qu'on a dit
        except sr.UnknownValueError:
            response="Aucun mot n'a été détecté. Je suis là pour vous aider.. Je peux afficher la liste des courses à faire, proposer des recettes, lister le contenu de votre frigo.. Je vous écoute !"
            error=1

        tts_play(response)                            # Jouer le son de ce qu'on a dit

        ###### Faire une pause selon les cas
        if error==1:
            time.sleep(13)
        else:
            time.sleep(2)
            
def tts_play(response):                                  ### To play text tranformed to Speech
    tts = gTTS(response, lang='fr', slow = False)        # Transform Speech to text 
    tts.save("response.mp3")                             # Save Speech
    p=vlc.MediaPlayer('response.mp3')                    # Play Speech with VLC
    p.play() 


# %%
################### Si tu veux activer le micro lance la fonction micro_activation()
micro_activation()


# %%



