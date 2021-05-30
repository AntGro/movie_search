import json
from datetime import date, timedelta
from json import JSONDecodeError

import bs4
import requests


def get_pages(token, nb, start_date):
    pages = {}
    w_date = start_date
    w = timedelta(days=7)
    for i in range(1, nb + 1):
        j = token + date.strftime(w_date, '%Y-%m-%d')
        pages[w_date] = j
        w_date += w
    return pages


def get_movie_info(movie_id: int):
    token = 'http://www.allocine.fr/film/fichefilm_gen_cfilm='
    response = requests.get(token + str(movie_id) + '.html')
    assert response.status_code == 200, response
    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    em_box = soup.find_all("script", {"type": "application/ld+json"})
    if len(em_box) == 0:
        return {}
    assert len(em_box) == 1, f'Got {len(em_box)} answers with movie id {movie_id}'
    try:
        movie_details = json.loads(em_box[0].contents[0], strict=False)
    except JSONDecodeError as e:
        print(em_box[0])
        raise e

    def extract_director(js_el):
        directors = []
        aux_directors = js_el['director']

        if not isinstance(aux_directors, list):
            aux_directors = [aux_directors]
        for el in aux_directors:
            directors.append(el['name'])
        return directors

    def extract_title(js_el):
        return js_el['name']

    return dict(titre=extract_title(movie_details), Réalisateur=extract_director(movie_details))


def get_theatre_infos(thetre_id: str):
    token = 'http://www.allocine.fr/seance/salle_gen_csalle='
    response = requests.get(token + str(thetre_id) + '.html')
    assert response.status_code == 200, response
    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    em_box = soup.find_all("span", {"class": "theater-cover-title"})
    assert len(em_box) == 1, len(em_box)
    name = em_box[0].contents[0]

    em_box = soup.find_all("div", {"class": "theater-cover-adress"})
    assert len(em_box) == 1, len(em_box)
    address = em_box[0].contents[0]

    em_box = soup.find_all("div", {"itemprop": 'paymentAccepted', "class": "card-type"})
    accepted_cards = {em.contents[0] for em in em_box}

    return dict(nom=name, adresse=address, cartes=accepted_cards)


def test_get_theatre_infos():
    theatre_info = get_theatre_infos('C0158')
    assert theatre_info['nom'] == 'Gaumont Parnasse', theatre_info['nom']
    assert theatre_info['adresse'] == "3, rue d'Odessa 75014 Paris", theatre_info['adresse']
    assert theatre_info['cartes'] == {'Chèque Cinéma Universel', 'CinéPass'}, theatre_info['cartes']


def get_seances(movie_id, city_id, day):
    return


if __name__ == '__main__':
    test_get_theatre_infos()
    token = 'http://www.allocine.fr/film/agenda/sem-'

    d = date(2021, 5, 22)
    n = 2
    pages = get_pages(token, n, d)

    movies = {}
    for d, content in pages.items():
        response = requests.get(content)
        assert response.status_code == 200, response
        soup = bs4.BeautifulSoup(response.text, 'html.parser')
        em_box = soup.find_all("a", {"class": "meta-title-link"})
        movies[d] = [(em['href'].split('=')[-1][:-5], em.contents[0]) for em in em_box]
    for date_out in movies:
        print(date_out)
        for movie in movies[date_out]:
            id, name = movie
            print(id, name, end=': ')
            infos = get_movie_info(id)
            print(infos)
    # TODO: extract more info
    # TODO: allow levenstein distance for request movie
    # TODO: utiliser un dataframe multi-index: date - film - infos - séances près de - horaires
    # TODO: build dataframe of movie theatre with accepted cards
    # TODO: have a set of movie makers to create alerts
