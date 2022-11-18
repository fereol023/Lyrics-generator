import networkx as nx
import matplotlib.pyplot as plt
import random


def charger_graphe(source):
    G = nx.Graph()
    fichier = open(source)
    fichier.readline()
    contenu = fichier.read()
    fichier.close()
    liste_couples = contenu.split("\n")
    for couple in liste_couples:
        couple_etudiants = couple.split(";")
        G.add_edge(couple_etudiants[0],couple_etudiants[1])
    return G


def generation_couleur_aleatoire(G):
    color_map = []
    for node in G:
        if random.randint(0,1) == 0:
            color_map.append('blue')
        else: 
            color_map.append('green')
    return color_map

def generation_couleur_themes(G, themes):
    color_map = []
    for node in G:
        if node in themes:
            color_map.append('red')
        else:
            color_map.append((0,0.4,0,1))
    return color_map

def generation_couleur_aretes_aleatoire(G):
    color_map = []
    for node in G.edges():
        if random.randint(0,1) == 0:
            color_map.append('red')
        else: 
            color_map.append('orange')
    return color_map

def change_taille_sommets(G):
    d = dict(nx.degree(G))
    node_s=[v * 10 for v in d.values()]
    return node_s


'''
G = charger_graphe("test.txt")

color_map = generation_couleur_aleatoire(G)
color_map_aretes = generation_couleur_aretes_aleatoire(G)

node_s = change_taille_sommets(G)
          
#nx.draw(G, with_labels=False,node_color=color_map,node_size=50)
nx.draw_shell(G, with_labels=False,node_size=node_s,node_color=color_map,edge_color=color_map_aretes)
#draw
#draw_random
#draw_shell
#draw_spectral

plt.savefig('plotgraph.png', dpi=300)
plt.show()

print("coucou les M2 !!!")
'''