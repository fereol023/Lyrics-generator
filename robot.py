from bs4 import BeautifulSoup
import requests, lxml


def requete_yahoo(chaine, destination):
    headers = {
        'User-agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582'
    }

    chaine = '"' + chaine + '"'
    # print("chaine a rechercher : ", chaine)

    params = {
        'p': chaine,
    }

    try:
        html = requests.get('https://fr.search.yahoo.com/search', headers=headers, params=params)
        fichier = open(destination, "w")
        fichier.write(html.text)
        fichier.close()

        if "Nous n'avons trouvé aucun résultat pour la recherche sur" in html.text:
            print("cette chaine n'obtient aucun resultat")
        nombre = html.text.split('<span style="color:inherit;" class=" fz-14 lh-22">')[1].split("</span>")[0]
        nombre = int(nombre.replace('\xa0', "").split(" ")[1].split("r")[0])
        # print("Nombre de résultats : ",nombre)
        return nombre

    # except UnicodeEncodeError:
    #    print("N'a pas pu écrire le résultat")

    except:
        nombre = 0
        # print("Nombre de résultats : ",nombre)
        return 0

    # requete_yahoo("delbot","resultat.html")
