""""
Auteurs : GBENOU Féréol / ATTIGNON Armande
M2 D3S
UNIVERSITE PARIS NANTERRE JAN 2023
"""

import random
import re
import nltk
from nltk import FreqDist
from collections import OrderedDict
import networkx as nx
import matplotlib.pyplot as plt
from robot import requete_yahoo
from math import log
import pandas as pd
import deepl


def join_func(sentence):
    """
    Joindre les chaînes de caractères en prenant en compte les stops words et les expressions régulières.
    """
    sentence = ' '.join(sentence)  # join normally
    sentence = re.sub(" ([,.;\):])", lambda m: m.group(1), sentence)  # retire l'espace à gauche
    sentence = re.sub("([\(]) ", lambda m: m.group(1), sentence)  # stick to right
    sentence = re.sub(" ([']) ", lambda m: m.group(1), sentence)  # join both sides
    return sentence


def liste_mots_ss_rep(texte):
    """
    Décompose un texte en mots. Retourne une liste de mots sans répétitions.
    """
    # print(len(list(set(nltk.word_tokenize(texte)))))
    return list(set(nltk.word_tokenize(texte, language="french")))


def liste_phrases(texte):
    """
    Décompose un texte en phrases. Retourne une liste de mots sans répétitions.
    """
    return list(nltk.sent_tokenize(texte, language="french"))


def selection_mots(words_list):
    """
    Parcours une liste et sélectionne les mots de moins de 10 lettres.
    (Pour éviter les mots trop longs.)
    """
    short_words_list = [m for m in words_list if len(m) < 10]
    # print(len(short_words_list))
    return short_words_list


def read_lyrics():
    """
    Lire le corpus de textes scrapés.
    """
    fichier = open('lyrics.txt')
    fichier.readline()
    raw = fichier.read()
    fichier.close()
    # le séparateur de textes correspond à celui qui est dans le scraper
    # lyrics = raw.split("\n \n   <|endoftext|>   \n \n")
    lyrics = raw.split("\n \n")
    # lyrics = [translator.translate_text(lyr, target_lang="FR").text for lyr in lyrics]
    # print(len(lyrics))
    return lyrics


def liste_mots_raw(texte):
    """
    Liste les mots présents dans un texte. Les ponctuations sont aussi considérées comme des mots.
    """
    return list(nltk.word_tokenize(texte))


def bigrams_decomposition(phrase):
    """
    Décompose un texte en groupes de deux mots.
    Le résultat est une liste unique de paires de mots qui se suivent.
    """
    pairs = nltk.bigrams(phrase)
    return list(set(pairs))


def generation_couleur_themes(G, themes):
    """
    Génère un mapping des couleurs des noeuds.
    Par défaut tous les noeuds ont la même couleur.
    Les mots de la liste themes ont une couleur différente.
    """
    color_map = []
    for node in G:
        if node in themes:
            color_map.append('red')
        else:
            color_map.append((0, 0.4, 0, 1))
    return color_map


def describe_graph(G):
    """
    Fonction décrivant un graphe orienté ou non.
    """
    print("\nCARACTERISTIQUES DU GRAPHE")
    print("Nombre d'arêtes : ", G.number_of_edges())
    print("Nombre de sommets : ", G.number_of_nodes())
    print("Densité de G : ", nx.density(G))
    print("Graphe connexe : ", nx.is_strongly_connected(G))
    H = G.copy()
    H = H.to_undirected()

    print("\nPlus longue des plus courtes phrases (diamètre) : ", nx.diameter(H))
    # si diamètre < log(G.number_of_nodes) : graphe petit monde
    if nx.diameter(H) < log(H.number_of_nodes()):
        print("---> Graphe petit monde")

    # ====distribution empirique des degrés
    dict_degres = dict(nx.degree(H))
    # print(dict_degres)
    data_degres = pd.DataFrame(data={"Degres": dict_degres.values()})
    print(data_degres.head())
    print("\nDISTRIBUTION EMPIRIQUE DES DEGRES")

    # percentiles
    perc = [0.2, 0.4, 0.5, 0.6, 0.8]
    # stats
    print(data_degres.describe(percentiles=perc))
    # si max(degré) < log(G.number_of_nodes) : graphe parcimonieux
    if max(dict_degres.values()) < log(H.number_of_nodes()):
        print("---> Graphe parcimonieux")
    dict_degres = sorted([v for v in dict_degres.items()], key=lambda t: t[1], reverse=True)
    degres, nb_degres = [d[0] for d in dict_degres if d[1] > 500], [d[1] for d in dict_degres if d[1] > 500]
    plt.plot(sorted(degres), nb_degres)
    plt.title("Distribution empirique des degrés")
    plt.savefig('Distrib_deg.png', dpi=300)
    # plt.show()
    # Fin description

# ======== PARTIE 1 : PRE TRAITEMENT ET VISUALISATION ========
# charger les lyrics : on obtient une liste de textes
m_lyrics = read_lyrics()
# faire une sélection du texte à utiliser
m_words = liste_mots_ss_rep(m_lyrics[0])
# on retire les mots longs (qui peuvent être des erreurs ou autres..)
s_words = selection_mots(m_words)
# distribution des mots
s_words_freq = FreqDist(s_words)

s_words_freq = OrderedDict(sorted(s_words_freq.items(), key=lambda t: t[1], reverse=True))
s_words_freq = {k: s_words_freq[k] for k in list(s_words_freq)}
# print(s_words_freq)

# === GRAPHE ===
edges_list = []
phrases = []

# --> utiliser une sélection de paragraphes pour la suite
# utiliser les regEx
m1 = m_lyrics[1]
m2 = m_lyrics[3]
m3 = m_lyrics[4]
    # application de deux expressions régulières

m1 = re.sub(r"(\w)[,;:!](\w)", r"\1 \2", m1)
m1 = re.sub(r"(\w)[,;:!]\s(\w)", r"\1 \2", m1)
t1 = liste_phrases(m1)

m2 = re.sub(r"(\w)[,;:!](\w)", r"\1 \2", m2)
m2 = re.sub(r"(\w)[,;:!]\s(\w)", r"\1 \2", m2)
t2 = liste_phrases(m2)

m3 = re.sub(r"(\w)[,;:!](\w)", r"\1 \2", m3)
m3 = re.sub(r"(\w)[,;:!]\s(\w)", r"\1 \2", m3)
t3 = liste_phrases(m3)

phrases = t1 + t2 + t3
s = len(phrases)
print(f"Sélection de {s} textes..")
# lister les mots par paragraphes (liste avec répétitions)
liste_mots_par_phrases = [liste_mots_raw(phr) for phr in phrases]
# faire des couples (mot, mot suivant) pour chaque mot de chaque paragraphe
raw_bgrams = [bigrams_decomposition(wphr) for wphr in liste_mots_par_phrases]
# ces paires de mots vont servir d'arêtes dans le graphe
# à noter : un mot est à prendre au sens large càd que les ponctuations sont aussi incluses
for wphr in raw_bgrams:
    for eij in wphr:
        edges_list.append(eij)

# initialisation du graphe orienté
GRAPHE = nx.DiGraph()
GRAPHE.add_edges_from(edges_list)
# visualisation
# --> dans themes on peut spécifier les mots/nœuds qu'on souhaite mettre en évidence à priori
map_couleur = generation_couleur_themes(GRAPHE, themes=[])
nx.draw(GRAPHE, with_labels=False, node_size=30, node_color=map_couleur, edge_color=(0.5, 0.5, 0.5, 0.5))
# plt.show()


# ======== PARTIE 2 : GENERATION DE TEXTES ========

# liste des mots qui commencent une phrase
start_words = [m for m in list(GRAPHE.nodes()) if GRAPHE.in_degree(m) == 0]
# liste des mots qui terminent une phrase
end_words = [m for m in list(GRAPHE.nodes()) if GRAPHE.out_degree(m) == 0]

# définir le nombre de phrases à écrire et un historique pour ne pas répéter les résultats
# max iter est la longueur maximale du texte si le processus ne s'arête pas
trials = 20
max_iter = 15
historique = []

for i in range(trials):
    phrase = []  # liste qui reçoit les mots à la suite
    longueur = 0  # compteur pour la taille de la phrase
    cont = True

    # COMMENCER LA PHRASE
    # on commence en choisissant un mot au hasard dans la liste des mots qui commencent une phrase
    w = random.choice(start_words)
    phrase.append(w)

    # à chaque étape, on se base sur le graphe et on choisit le mot suivant dans la liste des voisins possibles
    while cont:
        next_list = [m for m in GRAPHE.successors(w)]
        next_w = random.choice(next_list)
        # phrase.append(next_w.lower())
        phrase.append(next_w)
        longueur += 1  # pour actualiser la longueur de la phrase créée

        # TESTER LE SENS
        # ici on se base sur les mots présents dans la phrase en cours de création,
        # on considère des trios de mots consécutifs
        # on teste le sens de chaque trio au cours de la création en recherchant une correspondance sur internet
        # pour chaque trio, on enregistre le nombre de correspondances sur internet dans une liste,
        # on somme la liste,
        # ⇾ si le résultat est < à la valeur seuil, on retire le dernier mot ajouté.
        """
        if longueur >= 3:
            a_tester = bigrams_decomposition(phrase)
            a_tester = nltk.ngrams(phrase, n=3)
            S = [requete_yahoo(join_func(t), "rslt.html") for t in a_tester]
            X = 0
            for s in S:
                X += s
            if X == 0:
                del phrase[-1]
        

        if longueur % 2 == 0:
            a_tester = join_func(phrase)
            R = requete_yahoo(a_tester, "test.html")
            if R == 0:  # si la phrase actualisée n'a aucun sens, retirer le dernier mot
                del phrase[-1]
                longueur -= 1
        """
        # ensuite le mot dont on repart est le dernier mot de la phrase en cours
        w = phrase[-1]

        # FINIR LA PHRASE
        # le processus s'arrête de 2 manières
        # soit il poursuit la marche aléatoire jusqu'à tomber sur un mot qui termine une phrase
        if next_w in end_words:
            cont = False
        # soit, il s'arrête si la phrase en cours est trop longue : max_iter
        if longueur == max_iter:
            cont = False

    # fin du process
    phrase = join_func(phrase)
    if phrase not in historique:
        historique.append(phrase)
        print(phrase)

# écrire l'historique
output = open("phrases generees.txt", "w")
output.write("\n".join(historique))
output.close()

# ==== DESCRIPTION DU GRAPHE ======
describe_graph(GRAPHE)
plt.show()

