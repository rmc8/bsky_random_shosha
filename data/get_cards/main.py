import time

import pandas as pd
import requests as r
from bs4 import BeautifulSoup

URL: str = "https://www.aozora.gr.jp/index_pages/{path}"
UA: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.0.0 Safari/537.36"
headers: dict = {
    "User-Agent": UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
}


def card_collection(path: str) -> dict:
    url = URL.format(path=path)
    res = r.get(url, headers=headers)
    res.encoding = res.apparent_encoding
    bs = BeautifulSoup(res.text, "lxml")
    card_elms = bs.select("ol:nth-child(8) li a")
    for card_elm in card_elms:
        path = card_elm["href"].replace("../", "")
        if "person" in path:
            continue
        yield {
            "name": card_elm.text.strip(),
            "path": path,
        }


def get_contents_url(url) -> dict:
    res = r.get(url, headers=headers)
    res.encoding = res.apparent_encoding
    bs = BeautifulSoup(res.text, "lxml")
    links = bs.select("table.download a")
    res = {"zip_path": "", "html_path": ""}
    for link in links:
        if link.text.endswith(".zip"):
            res["zip_path"] = link.text.strip()
        elif link.text.endswith(".html"):
            res["html_path"] = link.text.strip()
    return res


def main():
    cnt = 0
    author_df = pd.read_csv("./data/get_cards/author_list.tsv", sep="\t")
    author_df = author_df[author_df["target_author"] == "Y"]
    table = []
    for author, path, _ in author_df.values.tolist():
        for card_dict in card_collection(path):
            cnt += 1
            print(cnt)
            record = {
                "card_path": card_dict["path"],
                "author": author,
            }
            url = f"https://www.aozora.gr.jp/{card_dict['path']}"
            contents_path_dict = get_contents_url(url)
            record.update(contents_path_dict)
            table.append(record)
            time.sleep(1)
    path: str = "./data/cards/card_list.html"
    df = pd.DataFrame(table)
    df.to_csv(path, sep="\t", index=False)


if __name__ == "__main__":
    main()
