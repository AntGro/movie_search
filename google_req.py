from time import sleep
from typing import Optional, List, Union, Iterable, Collection
from urllib.error import HTTPError

import bs4
import pandas as pd
import requests
import tqdm
from googlesearch import search

pd.set_option('display.max_rows', None, 'display.max_columns', None, 'display.max_colwidth', None)


def get_movie_id(movie):
    query = f"Allocine {movie}"

    result = []
    for j in search(query, tld='fr', lang='fr', num=1, start=0, stop=1, pause=0.1):
        result = j
    assert 'www.allocine.fr/film/fichefilm_gen_cfilm=' in result
    id = int(result.split('=')[1][:-5])
    return id


def get_city_id(city):
    query = f"Cinéma {city} Allociné"

    for j in search(query, tld='fr', lang='fr', num=1, start=0, stop=12, pause=0.1):
        if 'www.allocine.fr/salle/cinema/ville-' in j:
            result = j
            break

    assert 'www.allocine.fr/salle/cinema/ville' in result
    id = int(result.split('-')[1][:-1])
    return id


class NoResultFoundError(Exception):
    pass


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
    em_box = soup.find_all("span", {"itemprop": 'paymentAccepted', "class": "card-type"})
    accepted_cards.update({em.contents[0] for em in em_box})
    return dict(nom=name, adresse=address, cartes=accepted_cards)


def do_direct_request(movie, city, dates: Optional[Union[List[int], int]] = None):
    if dates is None:
        dates = []
    if isinstance(dates, int):
        dates = [dates]

    query = f"{movie} séances {city}"
    try:
        for j in search(query, tld='fr', lang='fr', num=3, start=0, stop=3, pause=0.1):
            if 'www.allocine.fr/seance/film-' in j:
                result = j
                break
            else:
                continue
    except HTTPError as e:
        raise RuntimeError(f"{query}\nAre you currently using a VPN?") from e

    results = [result]
    for d in dates:
        if d == 0:
            results.append(results[0])
        else:
            results.append(results[0] + f'd-{d}')
    return results[1:]


def explore_seance(seance_url: str, version: Optional[str] = None,
                   cards: Optional[Union[Iterable[str], str]] = None, progress_bar=None):
    if cards is None:
        cards = []

    seances = []

    get_res = True
    page = 1
    while get_res:
        url = seance_url
        if page > 1:
            url += f'?page={page}'
        response = requests.get(url)
        get_res = response.status_code == 200 and (page == 1 or (
                len(response.url.split('?')) > 1 and int(response.url.split('?')[1].split('=')[-1]) == page))
        if progress_bar is not None:
            progress_bar.tobeupd = f"Analysing page: {page} | "
        if get_res:
            soup = bs4.BeautifulSoup(response.text, 'html.parser')
            em_box = soup.find_all("div", {"class": "theater-card hred cf"})
            for theatre_res in tqdm.tqdm(em_box, leave=False, desc=f"Analysing page: {page}"):
                if progress_bar is not None:
                    progress_bar.tobeupd += '-'
                theatre_id = theatre_res.find('h2').find('a')['href'].split('=')[-1][:-5]

                theatre_cards = set(list(map(lambda card: card.lower(), get_theatre_infos(theatre_id)['cartes'])))
                good_cards = True
                for card in cards:
                    if card.lower() not in theatre_cards:
                        good_cards = False
                        break
                if not good_cards:
                    continue

                theatre_name = theatre_res.find('h2').text.split('\n')[1]
                theatre_adress = theatre_res.find('address').text
                for theatre_version_res in theatre_res.find_all("div", {'class': "showtimes-version"}):

                    aux = theatre_version_res.find_all("div", {'class': "text"})[0].text.split('\n')
                    date = ' '.join(aux[1].split()[:-1])
                    cur_version = aux[2].split()[-1]
                    if version is not None:
                        if version.lower() != cur_version.lower():
                            continue
                    for seance_time in theatre_version_res.find_all('span', {'class': "showtimes-hour-item-value"}):
                        seances.append((theatre_id, theatre_name, theatre_adress, ' / '.join(list(cards)), date,
                                        cur_version,
                                        seance_time.text))
                    for seance_time in theatre_version_res.find_all('span', {'class': "showtimes-hours-item-value"}):
                        seances.append(
                            (theatre_id, theatre_name, theatre_adress, ' / '.join(list(cards)), date, cur_version,
                             seance_time.text))

        page += 1
    return seances


def get_res(movie: str, city: str, dates: Union[List[int], int, None], cards: Collection[str],
            progress_bar, res_ph) -> pd.DataFrame:
    try:
        requests_ = do_direct_request(movie=movie, city=city, dates=dates)
    except Exception as e:
        progress_bar.tobeupd = f"{e.__class__}: {e.args[0]}"
        raise
    df_requests = []
    for request in requests_:
        results_ = explore_seance(request, cards=cards, progress_bar=progress_bar)
        aux_results = list(map(lambda x: (f'{x[1]} | {x[2]} | {x[3]}', *x[4:]), results_))
        df_request = pd.DataFrame(aux_results, columns=['Cinéma', 'Date', 'Version', 'Horaire']).set_index(
            ['Date', 'Cinéma', 'Version'])
        df_requests.append(df_request)
    aux = pd.concat(df_requests)
    res_ph[0] = aux
    return aux