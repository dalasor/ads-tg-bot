import requests
import json
from urllib.parse import urlencode
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
from config_data.config import Config, load_config
from database.database import user_dict_template, users_db

config: Config = load_config('.env')

ADS_TOKEN: str = config.tg_bot.ADS_TOKEN


def search_ads(q: str) -> list[str]:
    encoded_query = urlencode({'q': q, 'fl': 'bibcode'})
    results = requests.get("https://api.adsabs.harvard.edu/v1/search/query?{}&rows=2000".format(encoded_query),
                           headers={'Authorization': 'Bearer ' + ADS_TOKEN})
    bibcodes = [article['bibcode'] for article in results.json()['response']['docs']]
    return bibcodes


def check_bibcodes(bibcodes: list) -> list[str]:
    if len(bibcodes) == 0:
        return []
    else:
        return bibcodes  # Проверка на уже покзанные статьи, нужен отдельный файл который бдует считываться и сравниваться бибкоды


def export_ads(bibcodes: list) -> list[str]:
    if len(bibcodes) > 0:
        custom_format = "%3l  %T, %q, %V, [url: %u], [arxiv: %X], [abstract: %B]."
        payload = {'bibcode': bibcodes,
                   'format': custom_format,
                   'sort': 'first_author asc'}
        serialized_payload = json.dumps(payload)
        results = requests.post("https://api.adsabs.harvard.edu/v1/export/custom",
                                headers={'Authorization': 'Bearer ' + ADS_TOKEN},
                                data=serialized_payload)

        return results.json()['export'].split('\n')


def parse_info(articles: list[str]):
    names, urls, arxivs, abstracts, = [], [], [], []
    for i, a in enumerate(articles):
        names.append(f'<b><i>' + a[:a.find(", [url: ")] + '</i></b>.')
        urls.append(a[a.find(", [url: ") + 8:a.find("], [arxiv: ")])
        arxivs.append(a[a.find("], [arxiv: ") + 11:a.find("], [abstract: ")])
        abstracts.append(a[a.find(", [abstract: ") + 13:a.find("].")])
    return names, urls, arxivs, abstracts


def simple_query(pubdate: str) -> str:
    return 'abs:"primordial black holes" doctype:("article" OR "eprint" OR "inproceedings") ' + pubdate


def text_builder(user_id) -> (str, dict):
    start_index = 5 * (users_db[user_id]['current_page'] - 1)

    if (users_db[user_id]['current_page'] != users_db[user_id]['total_pages'] or
            len(users_db[user_id]['names']) % 5 == 0):
        end_index = start_index + 5
    else:
        end_index = start_index + users_db[user_id]['residue']

    names = users_db[user_id]['names']
    text = '\n\n'.join([f'<b>[<u>{str(i + 1)}</u>]</b> ' + name for i, name in enumerate(names)][start_index:end_index])
    n_btns = {str(v + 1): str(v + 1) for v in [i for i in range(start_index, end_index)]}

    return text, n_btns


def clean_latex(text: str) -> str:
    latex_pattern = re.compile(r'\$(.*?)\$')

    def replace_latex(match):
        latex_content = match.group(1).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("^", "&#94;")
        return f"<code>{latex_content}</code>"

    clean_text = latex_pattern.sub(replace_latex, text)

    return clean_text
