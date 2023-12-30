from typing import List

import pandas as pd
import requests as r
from bs4 import BeautifulSoup

URL: str = "https://www.aozora.gr.jp/index_pages/person_all.html"
UA: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.0.0 Safari/537.36"
headers: dict = {
    "User-Agent": UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
}


def get_author_list(path: str = "./target_author.txt") -> List[str]:
    with open(path, "r", encoding="utf-8") as f:
        return f.read().splitlines()


def main():
    author_list = get_author_list(path="./data/author_url/target_author.txt")
    res = r.get(url=URL, headers=headers)
    res.encoding = res.apparent_encoding
    bs = BeautifulSoup(res.text, "lxml")
    authors = bs.select("ol li a")
    table = []
    for author in authors:
        record = {
            "author_name": author.text,
            "path": author["href"].split("#")[0],
        }
        record["target_author"] = (
            "Y" if record["author_name"].replace(" ", "") in author_list else "N"
        )
        table.append(record)
    df = pd.DataFrame(table).drop_duplicates()
    df.to_csv("./data/get_cards/author_list.tsv", sep="\t", index=False)


if __name__ == "__main__":
    main()
