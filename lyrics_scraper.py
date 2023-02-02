import lyricsgenius as lg
# Auteur : https://github.com/johnwmillr/LyricsGenius

file = open("lyrics.txt", "w")  # fichier où sont enregistrés les lyrics
genius = lg.Genius('EkkQw7yQSphpb3R4n3CxWUZPUumF6DEWcm24v6t1FN91gKgPsbyy4hgmJqS1NBm4',
                             skip_non_songs=True, excluded_terms=["(Remix)", "(Live)"],
                             remove_section_headers=True)

#artists = ['Dinos']
artists = ['Youssoupha', 'Kery James']
#artists = ['Victor Hugo']


def get_lyrics(arr, k):  # Write lyrics of k songs by each artist in arr
    c = 0  # Counter
    for name in arr:
        try:
            songs = (genius.search_artist(name, max_songs=k, sort='popularity')).songs
            s = [song.lyrics for song in songs]
            # file.write("\n \n   <|endoftext|>   \n \n".join(s))  # Deliminator
            file.write("\n \n".join(s))
            file.write("\n".join(s))
            c += 1
            print(f"Songs grabbed:{len(s)}")
        except:
            # préviens s'il y a une erreur
            print(f"some exception at {name}: {c}")

get_lyrics(artists, 3)
