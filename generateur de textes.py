"""
Created on Sun Sep 18 11:30:33 2022

@author: gbeno
"""
import io
import random
import requests
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from math import log
from statistics import mean, stdev

# modules complémentaires
from preprocessing import liste_des_mots_debut, liste_des_mots_fin
from preprocessing import preparation_commentaires, filtrer_commentaires
from networkx_base import generation_couleur_aleatoire, generation_couleur_aretes_aleatoire
from networkx_base import generation_couleur_themes, change_taille_sommets
from robot import requete_yahoo

# pour la traduction
import deepl

auth_key = "59230f7d-a271-4748-2571-32a2d0e6c3c2:fx"
translator = deepl.Translator(auth_key)

line = "=======" * 5


def gen_graph(liste_mot_unique, dict_mots_accessibles, mat_freq, themes):
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
            # G.add_edge(key, v)
    print(line)
    print("CARACTERISTIQUES DU GRAPHE")
    print("Nombre d'arêtes : ", G.number_of_edges())
    print("Nombre de sommets : ", G.number_of_nodes())
    print("Densité de G : ", nx.density(G))
    if nx.is_strongly_connected(G): # teste la connexité
        print("Graphe connexe\nLongueur chemin max (diamètre) : ", nx.diameter(G))
        # si diamètre < log(G.number_of_nodes) : graphe petit monde
        if nx.diameter(G) < log(G.number_of_nodes()):
            print("Graphe petit monde")
    else:
        print("Graphe non connexe, diamètre infini")

    # ====distribution empirique des degrés
    # print(nx.degree(G))
    dict_degrees = dict(nx.degree(G))
    # print(dict_degrees)
    val_degrees = dict_degrees.values()
    # print(val_degrees)
    # valeurs uniques des degrés
    val_uniq_degrees = []
    for d in val_degrees:
        if d not in val_uniq_degrees:
            val_uniq_degrees.append(int(d))
    print("Degrés recensés : \n", sorted(val_uniq_degrees))
    # liste des frequences des degrés
    print("Fréquence absolues des degrés :\n", nx.degree_histogram(G))
    # autres statistiques empiriques
    print("Degré min : ", min(val_degrees))
    print("Degré max : ", max(val_degrees))
    print("Degré moyen (empirique) : ", mean(val_degrees))
    print("Ecart-type (empirique) : ", stdev(val_degrees))
    # si max(degré) < log(G.number_of_nodes) : graphe parcimonieux
    if max(val_degrees) < log(G.number_of_nodes()):
        print("Graphe parcimonieux")
    # plt.bar(np.arange(max(val_degrees)+1), nx.degree_histogram(G)/np.sum(nx.degree_histogram(G)))
    #plt.hist(nx.degree_histogram(G), density=True)
    #plt.title("Distribution empirique des degrés")
    #plt.savefig('plotgraph.png', dpi=300)
    #plt.show()

    # ====dessin graphe
    # color_map = generation_couleur_aleatoire(G)
    color_map_themes = generation_couleur_themes(G, themes)
    # color_map_aretes = generation_couleur_aretes_aleatoire(G)
    # node_s = change_taille_sommets(G)
    nx.draw(G, with_labels=False, node_size=30, node_color=color_map_themes, edge_color=(0.5,0.5,0.5,0.5))
    plt.savefig('plotgraph.png', dpi=300)
    plt.show()

def pick_forward(vector):
    L = []
    vector2 = []
    for v in vector:
        vector2.append(v)
    # print(vector2)

    for elt in vector:
        if elt != 0.:
            L.append(elt)
    # print(L)
    k = random.choice(L)
    return vector2.index(k), k


def creer_phrase1(mat_dist, liste_mots_uniq, mot_depart, longueur_phrase):
    ind_dep = liste_mots_uniq.index(mot_depart)
    k = 0
    phrase = []
    proba_phrase = 1
    ligne = mat_dist[ind_dep, ]
    phrase.append(liste_mots_uniq[ind_dep])

    while k < longueur_phrase:
        # choix d'un indice au hasard
        ind, prob = pick_forward(ligne)
        # print(ind)
        phrase.append(liste_mots_uniq[ind])
        # aller à la ligne du mot ayant cet indice
        ligne = mat_dist[ind, ]
        # calcul de la proba
        proba_phrase = proba_phrase * prob
        k += 1
    # print('ok')
    return phrase, proba_phrase


def creer_phrase2(mat_transition, liste_mots_uniq, max_iter=100):
    # on choisit un mot de depart au hasard dans la liste des debuts possibles
    mot_depart = random.choice(liste_des_mots_debut(comments))
    # on récupère son indice
    ind_depart = liste_mots_uniq.index(mot_depart)
    phrase = []  # on crée une phrase vide
    # et on ajoute le mot de départ à la phrase
    phrase.append(mot_depart)
    # on récupère la ligne de départ dans la matrice de transition
    ligne = mat_transition[ind_depart,]
    #
    proba_phrase = 1

    k = 0
    continuer = True
    while continuer and len(phrase) <= max_iter: # limiter la longueur des phrases pour éviter une marche infinie
        # choix d'un mot au hasard dans la liste des mots suivants possibles
        ind, prob = pick_forward(ligne)
        # print(ind)
        # ajout du mot choisi à la phrase en cours
        phrase.append(liste_mots_uniq[ind])
        # actualisation de la proba
        proba_phrase = proba_phrase * prob
        if liste_mots_uniq[ind] in liste_des_mots_fin(comments):
            continuer = False
        else:
            # aller à la ligne du mot ayant cet indice
            ligne = mat_transition[ind, ]
        k += 1
    # print('ok')
    return phrase, proba_phrase

def creer_phrase3(mat_transition, liste_mots_uniq, max_iter=30):
    # on choisit un mot de depart au hasard dans la liste des debuts possibles
    mot_depart = random.choice(liste_des_mots_debut(comments))
    # on récupère son indice
    ind_depart = liste_mots_uniq.index(mot_depart)
    phrase = []  # on crée une phrase vide
    # et on ajoute le mot de départ à la phrase
    phrase.append(mot_depart)
    # on récupère la ligne de départ dans la matrice de transition
    ligne = mat_transition[ind_depart,]
    #
    proba_phrase = 1

    k = 0
    continuer = True
    requete = 1 # initialisation
    while continuer and len(phrase) <= max_iter and requete > 0: # limiter la longueur des phrases pour éviter une marche infinie

        # Marche aléatoire
        print("Création...")
        # choix d'un mot au hasard dans la liste des mots suivants possibles
        ind, prob = pick_forward(ligne)
        # print(ind)
        # ajout du mot choisi à la phrase en cours
        phrase.append(liste_mots_uniq[ind])
        # actualisation de la proba
        proba_phrase = proba_phrase * prob
        if liste_mots_uniq[ind] in liste_des_mots_fin(comments):
            continuer = False
        else:
            # aller à la ligne du mot ayant cet indice
            ligne = mat_transition[ind, ]
        k += 1

        # test du contenu actuel de la phrase
        if k != 0:
            # test à chaque etape
            a_tester = " ".join(phrase)
            print("Testing... : ", a_tester)
            requete = requete_yahoo(a_tester, "test.html")
            print("Nombre de resultats (test) :", requete)
            if requete == 0:
                # supprimer le dernier mot ajouté et poursuivre
                del phrase[-1]

    # print('ok')
    return phrase, proba_phrase


def ecrire(trials, matrice_transition, liste_mots_uniques):
    """
    Fonction principale qui génère les phrases
    Elle écrit les phrases générées dans un fichier .txt
    """
    print("PHRASES GENEREES")
    fichier = open("phrases generees.txt", 'w')
    R = 0  # compteur de phrases sensées
    for i in range(trials):
        print(line)
        phrase, proba_phrase = creer_phrase3(matrice_transition, liste_mots_uniques)
        # print("Produit probas de transition : ", proba_phr1)
        phrase = " ".join(phrase)
        # result = translator.translate_text(phrase, target_lang="FR")
        # print(result.text)
        print("chaine a rechercher : ", '"'+phrase+'"')
        nombre = requete_yahoo(phrase, "resultat.html")
        print("Nombre de résultats : ", nombre)

        if nombre > 1: # toutes les phrases sont sur github
            R += 1
            fichier.write(phrase+"\n")
    fichier.close()
    print(line)
    print("Taux de phrases ayant une sémantique correcte : ", round(R * 100 / trials, 2), " %")


def poids_phrase(G, chemin):
    return nx.path_weight(G, chemin)


if __name__ == "__main__":
    # Lecture de la bdd
    # url = "https://raw.githubusercontent.com/fereol023/Comments-generator/main/vp_debate.csv"
    url = "https://raw.githubusercontent.com/fereol023/Comments-generator/main/all_debates.csv"
    download = requests.get(url).content
    df = pd.read_csv(io.StringIO(download.decode()))
    # print(df.head(10))
    # print(df.shape)

    # selection de la colonne de commentaires et prétraitement
    comments = df['comments'].values
    # comments = comments[450:700, ]  # 150 à 160
    themes = ["joe", "biden", "donald", "trump", "kamala", "harris", "mike", "pence", "obama", "barack"]
    comments = filtrer_commentaires(comments, themes)
    # print(comments)
    comments = comments[0].values

    # L : liste des mots uniques
    # D : dictionnaire des mots accessibles
    # T : matrice de transition
    L, D, T = preparation_commentaires(comments)
    gen_graph(L, D, T, themes)
    ecrire(100, T, L)


    # checker le sens au fur et a mesure que la phrase est construite et s'arreter dès que le resultat de la requete = 0
    # he
    # he is
    # he is repeating
    # he is repeating new