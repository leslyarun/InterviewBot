# -*- coding:utf8 -*-
# !/usr/bin/env python

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os
import interviewbot as bot
from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)

copiedtracker = []
scoretracker = []
finaltext = []


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    # print("Request:")
    # print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    if req.get("queryResult").get("action") == "qs":
        res = interview_qs(req)
        print("response is", res)
        return res

    elif req.get("queryResult").get("action") == "bye":
        for index, item in enumerate(copiedtracker):
            finaltext.append(
                """Here are the Test Results: Qs.""" + str(index + 1) + """ - Answer copied - """ + str(item))
            print("""Here are the Test Results:
            Qs.""" + str(index + 1) + """ - Answer copied - """ + str(item))

        for index, item in enumerate(scoretracker):
            finaltext.append("""Score for every answer: Qs.""" + str(index + 1) + """ - Score is """ + str(item))
            print("""Score for every answer:
             Qs.""" + str(index + 1) + """ - Score is """ + str(item))

        return {
            "fulfillmentText": finaltext
        }
    else:
        return {}


def interview_qs(req):
    qs_idx = bot.random_qs_index()
    copiedtracker.append(copiedornot(req, qs_idx))
    scoretracker.append(answerscore(req, qs_idx))
    qs = bot.random_question(qs_idx)
    return {
        "fulfillmentText": qs
    }


def copiedornot(req, qs_idx):
    qs = bot.random_question(qs_idx)
    links = bot.google_links(qs)
    texts = bot.get_link_text(links)
    answer = req.get("queryResult").get("queryText")
    copied = bot.is_copied(texts, answer)
    if copied:
        print("Answer copied from Google")
    return copied


def answerscore(req, qs_idx):
    qs = bot.random_question(qs_idx)
    answer = req.get("queryResult").get("queryText")
    ans_tokens = bot.answer_tokens(answer)
    orig_ans_tokens = bot.original_ans_tokens(qs_idx)
    simscore = bot.similarity_check(ans_tokens, orig_ans_tokens)
    keywords = bot.key_matching(qs_idx)
    keysimscore = bot.key_similarity_check(keywords, ans_tokens)
    matches = bot.match_score(keywords, ans_tokens)
    alternatescore = bot.alternate_score(keywords, matches)
    return {
        "similarityScore": simscore,
        "keySimilarityScore": keysimscore,
        "alternateScore": alternatescore
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=True, port=port, host='0.0.0.0')
