"""
Created on Sun Sep 18 11:30:33 2022

@author: gbeno
"""

import numpy as np
import pandas as pd
import requests
import io

from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra
from collections import Counter

line = "======="*5

def liste_mots_par_commentaire(comments) :
    '''
    A partir des commentaires (colonne pandas), génère une liste l1 de liste l2.
    l1 est la liste des phrases
    l2 est la liste des mots dans une phrase
    '''
    for i in range(len(comments)) : 
        liste_de_mots = []
        for comment in comments : 
            mot = comment.split(sep=" ")
            liste_de_mots.append(mot)
    return liste_de_mots


def liste_mots_exhaustive(comments) : 
    '''
    Renvoie une liste qui contient tous les mots employés dans comments sans répétition
    '''
    liste_de_mots = []
    for comment in comments : 
        phrase = comment.split(sep=" ")
        for mot in phrase :
            # ajoute si le mot n'était pas présent dans la liste
            if mot not in liste_de_mots :    
                liste_de_mots.append(mot)
            #print(liste_de_mots)
    # ajouter un "." car utile après
    liste_de_mots.append(".")
    return liste_de_mots


def mots_accessibles(cle, liste_mots_par_commentaire) : 
    '''
    Renvoie la liste des mots accessibles depuis le mot cle dans la liste des 
    commentaires
    '''
    liste_mots_accessibles = []
    for phrase in liste_mots_par_commentaire :
        #print(phrase)
        for mot in phrase :
            if mot == cle :
                # récupere l'indice du mot 
                index = phrase.index(mot)
                #print(mot, index)
                index += 1 
      
                #/!\ si c'est le dernier mot de la phrase le mot_a_droite devient un "."
                if index == len(phrase) : 
                    mot_a_droite = "."
                else :
                    mot_a_droite = phrase[index]
      
                #print(mot_a_droite)
                # ajoute à la liste des mots accessibles depuis la clé
                # si le mot n'est pas déja dans la liste
                if mot_a_droite not in liste_mots_accessibles :
                    liste_mots_accessibles.append(mot_a_droite)
                    
            else : 
                pass
            
    return liste_mots_accessibles

def dict_mots_accessibles(liste_mots_exhaustive, liste_mots_par_commentaire) :
    # pour chaque mot dans la liste des mots unique, on considère le mot 
    # comme clé et on applique la fonction mots_accessibles
    D1 = {}
    for i in range(len(liste_mots_exhaustive)) : 
        cle = liste_mots_exhaustive[i]
        mots_atteignables = mots_accessibles(cle, liste_mots_par_commentaire)
        D1[cle] = mots_atteignables
    #print(D1)
    return D1
        
        
def vect_freq(cle, liste_mots_exhaustive, liste_mots_par_commentaire) :
    # retourne une liste en sortie 
    # initialise un vecteur vide de même longueur que la liste exhaustive de mots
    vect = [0]*len(liste_mots_exhaustive)
    #print(vect)
    # liste les mots acessibles depuis cette clé
    cle_mots_atteignables = mots_accessibles(cle, liste_mots_par_commentaire)
    #print(cle_mots_atteignables)
    # compte le nombre d'occurences de chaque mot atteignable
    D = Counter(cle_mots_atteignables)
    #print(D)
    
    for mot in list(D.keys()) :
        # pour chaque mot atteignable, obtenir l'indice du mot dans la liste exhaustive
        indice = liste_mots_exhaustive.index(mot)
        # utiliser l'indice pour inputer le nombre d'occurences
        vect[indice] = D[mot]
    
    #print(vect)
    return vect
    

def dico_freq(liste_mots_exhaustive, liste_mots_par_commentaire) :
    # retourne un dictionnaire des frequences des mots à droite
    Dico_freq = dict()
    
    #for mot in liste_mots_exhaustive : 
    #    Dico_freq[mot] = vect_freq(mot, liste_mots_exhaustive, liste_mots_par_commentaire)
    
    for j in range(len(liste_mots_exhaustive)) :
        mot_cle = liste_mots_exhaustive[j]
        Dico_freq[mot_cle] = vect_freq(mot_cle, liste_mots_exhaustive, liste_mots_par_commentaire)
    
    return Dico_freq


def preparation_commentaires(comments) :
    '''
    fonction de preparation des commentaires
    -----------
    parametres :
    une colonne de commentaires format pandas
    -----------
    renvoie :
    1- la liste exhaustive des mots uniques
    2- un dictionnaire des mots accessibles de puis chaque mot : voisins sortants
    3- une matrice des frequences/probas : poids
    '''
    l_mpc = liste_mots_par_commentaire(comments)
    l_mots_uniques = liste_mots_exhaustive(comments)
    
    d_mots_access = dict_mots_accessibles(l_mots_uniques, l_mpc)
    d_freq_mots_access = dico_freq(l_mots_uniques, l_mpc) 
    
    
    print(line)
    print("LISTE DES EXHAUSTIVE MOTS")
    print(l_mots_uniques)
    print(len(l_mots_uniques))
    print(line)
    print("DICT DES MOTS SUIVANTS")
    for d in d_mots_access.items():
        print(d)
    
    mat_freq = []
    # ajouer la liste des frequences pour faire un tableau
    for elt in d_freq_mots_access.values() :
        mat_freq.append(elt)
    
    print(line)
    print("FREQ DES MOTS SUIVANTS")
    # conversion en numpy array 
    print(np.array(mat_freq))
    
    
    return l_mots_uniques, d_mots_access, np.array(mat_freq)
    
if __name__=="__main__" :
    # Lecture de la bdd
    url = "https://raw.githubusercontent.com/fereol023/Comments-generator/main/vp_debate.csv"
    download = requests.get(url).content
    df = pd.read_csv(io.StringIO(download.decode()))
    print(df.head(10))
    
    # selction de la colonne de commentaires
    comments = df['comments'].values
    comments = comments[100:150,]
    print(comments)
    
    #liste_mots_par_commentaire = liste_mots_par_commentaire(comments)
    #print(liste_mots_par_commentaire)
    
    #liste_mots_exhaustive = liste_mots_exhaustive(comments)
    #print(liste_mots_exhaustive)

    # compteur de mots et renvoie un dict avec le nombre d'occurences
    #occurrences = Counter(liste_mots_exhaustive)
    #print(occurrences)
    # PS supprimer lesmots trop longs
    
    # enregister la liste des valeurs uniques des mots
    #mots_uniques = list(occurrences.keys())
    #print(mots_uniques)
    
    # liste des mots accessibles depuis une clé
    #a = mots_accessibles("harris", liste_mots_par_commentaire)
    #print(line)
    #print(a)
    
    # dictionnaire de l'ensemble des mots accessibles depuis un mot
    #D1 = dict_mots_accessibles(liste_mots_exhaustive, liste_mots_par_commentaire)
    #print(D1["trump"])
    
    # dictionnaire des fréquences des mots atteignables
    #print(line)
    #vect_freq("famous", liste_mots_exhaustive, liste_mots_par_commentaire)
    #dico_freq(liste_mots_exhaustive, liste_mots_par_commentaire)
    
    e1, e2, e3 = preparation_commentaires(comments)

    #################
    # instancier un graphe avec la matrice eparse
    G = csr_matrix(e3)
    # appliquer l'algo de dijkstra
    dist_matrix, predecessors = dijkstra (csgraph = G, directed = True,
                                          return_predecessors = True)
    print(line)
    print("MATRICE DES DISTANCES")
    print(dist_matrix)
    print("Taille de la matrice : ", dist_matrix.shape)
    
    
    # *****************************
    #->selectionner uniquement les mots qui ont une longueur mamximale de 10 lettres (moyenne en anglais)
    