# cd data/create_contents
import os
import re
import json
import random
from os.path import dirname, abspath
from glob import glob
import pathlib

import spacy
import requests as r
from bs4 import BeautifulSoup
import pandas as pd


script_path = dirname(abspath(__file__))
contents_path = str(pathlib.Path(f"{script_path}/../../contents/").resolve())
nlp = spacy.load("ja_core_news_sm")


def get_url_list():
    url_text = f"{script_path}/urls.txt"
    with open(url_text, "r") as f:
        return f.read().splitlines()


def contents_list():
    l = glob(f"{contents_path}/**/**.json")
    return [f.split("/")[-1].replace(".json", ".html") for f in l]


def get_new_url_list():
    exists_contents = contents_list()
    table_txt = f"{script_path}/../cards/card_list.tsv"
    df = pd.read_csv(table_txt, sep="\t")
    df = df[~df["html_path"].isin(exists_contents)]
    print(len(df))
    data = random.sample(list(df.to_dict(orient="records")), 100)
    for rec in data:
        path = "/".join(rec["card_path"].split("/")[:-1])
        url = f"https://www.aozora.gr.jp/{path}/files/{rec['html_path']}"
        yield url


def get_sentence(text):
    contents = []
    for sent in nlp(text).sents:
        if str(sent).count("「") != str(sent).count("」"):
            continue
        if str(sent).count("（") != str(sent).count("）"):
            continue
        if str(sent).count("『") != str(sent).count("』"):
            continue
        if str(sent)[0] == "」" or str(sent)[0] == "』" or str(sent)[0] == "）":
            continue
        if len(sent) <= 15 or 80 < len(sent):
            continue
        contents.append(re.sub(r"［＃.*?］", "", str(sent).strip()))
    return contents


def get_ids(url: str):
    l = url.split("/")
    author_id = l[4]
    contents_id = l[-1].replace(".html", "")
    return author_id, contents_id


def main():
    ADD_CONTENTS_LIMIT = 50
    cnt = 0
    urls = list(get_new_url_list())
    for url in urls:
        res = r.get(url)
        res.encoding = res.apparent_encoding
        bs = BeautifulSoup(res.text, "xml")
        if bs.select_one(".title") is None:
            continue
        try:
            title = bs.select_one(".title").text
            author = bs.select_one(".author").text
            raw_data = bs.select_one(".main_text").text
            contents = re.sub(r"（[ぁ-んァ-ヶ]+）", "", raw_data)
        except AttributeError as e:
            continue
        try:
            data = get_sentence(contents)
            if not data:
                print("No data")
                continue
        except Exception as e:
            print(e)
            continue
        rec = {
            "title": title,
            "author": author,
            "url": url,
            "contents": data,
        }
        author_id, contents_id = get_ids(url)
        dir_path = f"{contents_path}/{author_id}"
        output_path = f"{dir_path}/{contents_id}.json"
        os.makedirs(dir_path, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            print(json.dumps(rec, ensure_ascii=False, indent=4), file=f)
        print(f"Done: {output_path}")
        cnt += 1
        if cnt >= ADD_CONTENTS_LIMIT:
            break


if __name__ == "__main__":
    main()