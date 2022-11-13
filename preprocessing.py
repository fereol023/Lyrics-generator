import numpy as np
import pandas as pd
from collections import Counter

line = "=======" * 5

def filtrer_commentaires(comments, themes):
    """
    Filtre la liste des commentaires suivant la liste des themes
    Retire les commentaires qui contiennent un mot qui commence par "https"
    Retire les doublons
    """
    print("Nombre initial de commentaires : ", len(comments))
    filtered_comments = []
    # ====themes
    for text in comments:
        text = text.split(" ")
        for mot in text:
            if mot in themes:
                filtered_comments.append(" ".join(text))
    # ====https et doublons
    filtered_comments2 = []
    counts = []
    for text in filtered_comments:
        count = 0
        text = text.split(" ")
        for mot in text:
            if mot.startswith("https"):
                # compte le nombre de mots qui commencent par https
                count += 1
        counts.append(count)
        if count == 0 and " ".join(text) not in filtered_comments2:
            # on garde uniquement les commentaires dont count est 0 et
            # qui ne sont pas déjà présents dans la liste
            filtered_comments2.append(" ".join(text))
            # print(" ".join(text)+"\n")
    print("Nombre de commentaires après filtres : ", len(filtered_comments2))
    print(line)
    return pd.DataFrame(filtered_comments2)


def liste_mots_par_commentaire(comments):
    """
    À partir des commentaires (colonne pandas), génère une liste l1 de liste l2.
    l1 : la liste des phrases
    l2 : la liste des mots dans une phrase
    """
    for i in range(len(comments)):
        liste_de_mots = []
        for comment in comments:
            mot = comment.split(sep=" ")
            liste_de_mots.append(mot)
    return liste_de_mots


def liste_mots_exhaustive(comments):
    '''
    Renvoie une liste qui contient tous les mots employés dans comments sans répétition
    '''
    liste_de_mots = []
    for comment in comments:
        phrase = comment.split(sep=" ")
        for mot in phrase:
            # ajoute si le mot n'était pas présent dans la liste
            if mot not in liste_de_mots:
                liste_de_mots.append(mot)
            # print(liste_de_mots)
    # ajouter un "." car utile après
    liste_de_mots.append(".")
    return liste_de_mots


def liste_des_mots_debut(comments):
    """
    Cette fonction donne la liste des mots qui commencent une phrase
    """
    debuts = []
    for comment in comments:
        phrase = comment.split(sep=" ")
        debuts.append(phrase[0])
    return debuts


def liste_des_mots_fin(comments):
    """
    Cette fonction donne la liste des mots qui commencent une phrase
    """
    fins = []
    for comment in comments:
        phrase = comment.split(sep=" ")
        fins.append(phrase[-1])
    fins.append(".")
    return fins


def mots_accessibles(cle, liste_mots_par_commentaire):
    '''
    Renvoie la liste des mots accessibles depuis le mot cle dans la liste des
    commentaires
    '''
    liste_mots_accessibles = []
    for phrase in liste_mots_par_commentaire:
        # print(phrase)
        for mot in phrase:
            if mot == cle:
                # récupere l'indice du mot
                index = phrase.index(mot)
                # print(mot, index)
                index += 1

                # /!\ si c'est le dernier mot de la phrase le mot_a_droite devient un "."
                if index == len(phrase):
                    mot_a_droite = "."
                else:
                    mot_a_droite = phrase[index]

                # print(mot_a_droite)
                # ajoute à la liste des mots accessibles depuis la clé
                # si le mot n'est pas déja dans la liste
                if mot_a_droite not in liste_mots_accessibles:
                    liste_mots_accessibles.append(mot_a_droite)

            else:
                pass

    return liste_mots_accessibles


def dict_mots_accessibles(liste_mots_exhaustive, liste_mots_par_commentaire):
    # pour chaque mot dans la liste des mots unique, on considère le mot
    # comme clé et on applique la fonction mots_accessibles
    D1 = {}
    for i in range(len(liste_mots_exhaustive)):
        cle = liste_mots_exhaustive[i]
        mots_atteignables = mots_accessibles(cle, liste_mots_par_commentaire)
        D1[cle] = mots_atteignables
    # print(D1)
    return D1


def vect_freq(cle, liste_mots_exhaustive, liste_mots_par_commentaire):
    # retourne une liste en sortie
    # initialise un vecteur vide de même longueur que la liste exhaustive de mots
    vect = [0] * len(liste_mots_exhaustive)
    # print(vect)
    # liste les mots acessibles depuis cette clé
    cle_mots_atteignables = mots_accessibles(cle, liste_mots_par_commentaire)
    # print(cle_mots_atteignables)
    # compte le nombre d'occurences de chaque mot atteignable
    D = Counter(cle_mots_atteignables)
    # print(D)

    for mot in list(D.keys()):
        # pour chaque mot atteignable, obtenir l'indice du mot dans la liste exhaustive
        indice = liste_mots_exhaustive.index(mot)
        # utiliser l'indice pour inputer le nombre d'occurences
        vect[indice] = D[mot]

    # print(vect)
    return vect


def dico_freq(liste_mots_exhaustive, liste_mots_par_commentaire):
    # retourne un dictionnaire des frequences des mots à droite
    Dico_freq = dict()

    # for mot in liste_mots_exhaustive :
    #    Dico_freq[mot] = vect_freq(mot, liste_mots_exhaustive, liste_mots_par_commentaire)

    for j in range(len(liste_mots_exhaustive)):
        mot_cle = liste_mots_exhaustive[j]
        Dico_freq[mot_cle] = vect_freq(mot_cle, liste_mots_exhaustive, liste_mots_par_commentaire)

    return Dico_freq


def preparation_commentaires(comments):
    """
    Fonction de preparation des commentaires à partir
    d'une colonne de commentaires format pandas
    ============================================
    Renvoie :
    1- la liste exhaustive des mots uniques
    2- un dictionnaire des mots accessibles depuis chaque mot : voisins sortants
    3- une matrice des frequences/probas : poids
    """
    # ====Listes de mots
    l_mpc = liste_mots_par_commentaire(comments)
    l_mots_uniques = liste_mots_exhaustive(comments)
    print("LISTE DES EXHAUSTIVE MOTS UNIQUES")
    print("Nombre de mots : ", len(l_mots_uniques))
    print(l_mots_uniques)

    # ====Dictionnaire des mots accessibles
    d_mots_access = dict_mots_accessibles(l_mots_uniques, l_mpc)
    d_freq_mots_access = dico_freq(l_mots_uniques, l_mpc)
    print(line)
    print("DICTIONNAIRE DES MOTS SUIVANTS")
    for d in d_mots_access.items():
        print(d)

    # ====Matrice de transition
    mat_freq = []
    # ajouter la liste des frequences absolues pour faire un tableau
    for elt in d_freq_mots_access.values():
        mat_freq.append(elt)

    mat_freq = np.array(mat_freq, dtype=object)
    # calculer les frequences relatives en divisant par le nombre de mots sur la ligne
    denom = np.sum(mat_freq, axis=1)
    denom[-1] = 1  # pour la ligne de '.' qui n'a que des zéros
    # print(np.sum(mat_freq, axis=1))
    mat_freq = mat_freq / denom
    print(line)
    print("MATRICE DE TRANSITION")
    print("Taille de la matrice : ", mat_freq.shape)
    print(mat_freq)
    return l_mots_uniques, d_mots_access, mat_freq


