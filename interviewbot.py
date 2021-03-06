import numpy as np
import pandas as pd
import urllib.request
from bs4 import BeautifulSoup
from googlesearch import search
import os
from urllib.request import Request, urlopen

# package = sputnik.install('spacy', spacy.about.__version__, spacy.about.__download_url__)

# nlp = spacy.load('en_core_web_sm')
import en_core_web_sm

nlp = en_core_web_sm.load()

# Read the Qs.Bank Dump
my_path = os.path.abspath(os.path.dirname(__file__))
path = os.path.join(my_path, "java_sample-qs.xlsx")
df = pd.read_excel(path)


def random_qs_index():
    qs_idx = np.random.randint(0, (len(df) - 1))
    return qs_idx


def random_question(qs_idx):
    qs = df['Question'][qs_idx]
    return qs


def answer_tokens(ans):
    ans_tokens = nlp(ans)
    return ans_tokens


def original_ans_tokens(qs_idx):
    orig_ans = df['Answer'][qs_idx]
    orig_ans_tokens = nlp(orig_ans)
    return orig_ans_tokens


# Check Similarity
def similarity_check(token1, token2):
    sim = token1.similarity(token2)
    return sim


# Keywords matching - Answer tokens vs keywords to produce a score
def key_matching(qs_idx):
    keywords = df['Keywords'][qs_idx]
    keywords = nlp(keywords)
    return keywords


def key_similarity_check(keywords, ans_tokens):
    score = keywords.similarity(ans_tokens)
    return score


# Another approach to calculate score
def match_score(keywords, ans_tokens):
    matches = 0
    for k in keywords.text.split():
        if k in list(ans_tokens.text.split()):
            print(k, 'is found in answer')
            matches += 1
    print('matches = ', matches)
    return matches


# Alternate score
def alternate_score(keywords, matches):
    total = len(keywords)
    if matches != 0:
        alt_score = total // matches
        return alt_score
    else:
        return 0


def google_links(qs):
    # to search
    query = qs

    links = []

    for j in search(query, tld="co.in", num=10, stop=1, pause=2):
        links.append(j)

    return links


def get_link_text(links):
    texts = []
    for link in links:
        req = Request(link, headers={'User-Agent': 'Mozilla/5.10'})
        req.add_header('Accept',
                       'application/json,text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
        try:
            soup = BeautifulSoup(urllib.request.urlopen(req), "html5lib")
            # print(soup.text)
            texts.append(soup.text)
        except:
            continue

    return texts


def is_copied(texts, ans):
    for text in texts:
        return ans in text
