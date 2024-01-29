from os.path import dirname, abspath
from glob import glob
import pathlib

import pandas as pd


script_path = dirname(abspath(__file__))
contents_path = str(pathlib.Path(f"{script_path}/../../contents/").resolve())


def contents_list():
    return glob(f"{contents_path}/**/**.json")


def main():
    contents = contents_list()
    data = []
    for content in contents:
        author_id, content_id = content.split("/")[-2:]
        data.append({
            "author_id": author_id,
            "content_id": content_id,
        })
    df = pd.DataFrame(data)
    df.to_csv(f"{script_path}/contents_table.tsv", sep="\t", index=False)
    print(f"作品数：{len(contents)}")
    print(f"お題の数：")


if __name__ == "__main__":
    main()
