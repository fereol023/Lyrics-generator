"""
Created on Sun Sep 18 11:30:33 2022

@author: gbeno
"""
import random
import numpy as np
import pandas as pd
import requests
import io

import networkx as nx
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra
import matplotlib.pyplot as plt
from collections import Counter

# module complémentaire
from networkx_base import generation_couleur_aleatoire, generation_couleur_aretes_aleatoire, change_taille_sommets

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
    2- un dictionnaire des mots accessibles depuis chaque mot : voisins sortants
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
    
    mat_freq = np.array(mat_freq)
    # calculer les freq relatives en divisant par le nombre de mots sur la ligne
    denom = np.sum(mat_freq, axis=1)
    denom[-1] = 1 # pour la ligne de '.' qui n'a que des zéros
    #print(np.sum(mat_freq, axis=1))
    mat_freq = mat_freq/denom
    print(line)
    print("FREQ DES MOTS SUIVANTS")
    # conversion en numpy array 
    print(mat_freq)
    print("Taille de la matrice : ",mat_freq.shape)

    return l_mots_uniques, d_mots_access, mat_freq

def gen_graph(dict_mots_accessibles) :
    
    G = nx.DiGraph()
    # ajout des sommets au graphe
    G.add_nodes_from(list(dict_mots_accessibles.keys()))
    # création des aretes
    for key in dict_mots_accessibles.keys() :
        mots_access = dict_mots_accessibles[key]
        for v in mots_access :
            G.add_edge(key, v)
    
    # dessin
    color_map = generation_couleur_aleatoire(G)
    color_map_aretes = generation_couleur_aretes_aleatoire(G)
    node_s = change_taille_sommets(G)
    nx.draw(G, with_labels=False, node_size=node_s,node_color=color_map,edge_color=color_map_aretes)

    plt.savefig('plotgraph.png', dpi=300)
    plt.show()

def gen_graph2(liste_mot_unique, dict_mots_accessibles, mat_freq) :

    G = nx.DiGraph()
    # ajout des sommets au graphe
    G.add_nodes_from(list(dict_mots_accessibles.keys()))
    # création des aretes
    for key in dict_mots_accessibles.keys():
        mots_access = dict_mots_accessibles[key]
        for v in mots_access:
            ind_row = liste_mot_unique.index(key)
            ind_col = liste_mot_unique.index(v)
            # recuperer le poids depuis la matrice
            poids = mat_freq[ind_row, ind_col]
            # creer l'arete
            G.add_edge(key, v, weight=poids)
            #G.add_edge(key, v)

    # dessin
    color_map = generation_couleur_aleatoire(G)
    color_map_aretes = generation_couleur_aretes_aleatoire(G)
    node_s = change_taille_sommets(G)
    nx.draw(G, with_labels=False, node_size=node_s,node_color=color_map,edge_color=color_map_aretes)
    plt.savefig('plotgraph.png', dpi=300)
    plt.show()

def pick_forward(vector):
    #vector = np.array([0, 0, 5, 5, 6, 0, 8])
    #vector = vector / np.sum(vector)
    L = []
    vector2 = []

    for v in vector:
        vector2.append(v)
    #print(vector2)

    for elt in vector:
        if elt != 0.:
            L.append(elt)
    # print(L)
    k = random.choice(L)
    return vector2.index(k)

def creer_phrase1(mat_dist, liste_mots_uniq, mot_depart, longueur_phrase):

    ind_dep = liste_mots_uniq.index(mot_depart)
    k = 0
    phrase = []
    ligne = mat_dist[ind_dep, ]
    phrase.append(liste_mots_uniq[ind_dep])

    while k < longueur_phrase:
        # choix d'un indice au hasard
        ind = pick_forward(ligne)
        #print(ind)
        phrase.append(liste_mots_uniq[ind])
        # aller à la ligne du mot ayant cet indice
        ligne = mat_dist[ind, ]
        k += 1
    print('ok')

    return phrase

if __name__=="__main__" :
    # Lecture de la bdd
    url = "https://raw.githubusercontent.com/fereol023/Comments-generator/main/vp_debate.csv"
    download = requests.get(url).content
    df = pd.read_csv(io.StringIO(download.decode()))
    print(df.head(10))
    print(df.shape)
    
    # selction de la colonne de commentaires
    comments = df['comments'].values
    #comments = comments[150:172,]  # 150 à 151 160 170:172 # peu pas afficher + de 500 points
    print(comments)
    
    # liste_mots_par_commentaire = liste_mots_par_commentaire(comments)
    # print(liste_mots_par_commentaire)
    #
    # liste_mots_exhaustive = liste_mots_exhaustive(comments)
    # print(liste_mots_exhaustive)
    # print(len(liste_mots_exhaustive))
    #
    # dico_mots_accessibles = dict_mots_accessibles(liste_mots_exhaustive, liste_mots_par_commentaire)
    # gen_graph(dico_mots_accessibles)

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

    #gen_graph2(e1, e2, e3)


    #################
    # instancier un graphe avec la matrice eparse
    M = csr_matrix(e3)
    # appliquer l'algo de dijkstra
    dist_matrix = dijkstra(csgraph=M, directed=True, return_predecessors=False)
    print(line)
    print("MATRICE DES DISTANCES")
    print(dist_matrix)
    print(line)
    #print("MATRICE DES PREDECESSEURS")
    #print(predecessors)
    #print("Taille de la matrice : ", dist_matrix.shape)

    # essai création phrase
    cle = "kamala"
    p1 = creer_phrase1(e3, e1, cle, 10)
    print(p1)

    ## >>>> next step mettre la phrase + proba de la phrase = produit des probas de la matrice
    ## >>>> also : modifier la fonction creer_phrase1() pour qu'elle prenne le mot en paramètre directement
    #print(e1.index('harris'))
    # *****************************
    #->selectionner uniquement les mots qui ont une longueur maximale de 10 lettres (moyenne en anglais)
    
    