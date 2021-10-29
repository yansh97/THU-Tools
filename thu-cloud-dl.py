#!/usr/local/Caskroom/miniconda/base/bin/python

from typing import List, Tuple
import requests
import json
import re
from urllib.parse import quote
import os
import click
from tqdm import tqdm


def fs(bytes: int) -> str:
    assert bytes >= 0
    num = bytes
    for suffix in ["B", "KB", "MB", "GB", "TB"]:
        if num < 1024.0:
            return f"{num:.2f}{suffix}"
        num /= 1024.0
    return f"{num:.2f}PB"


def search_entries(
    exclude_ext_list: List[str],
    share_id: str,
    root_dir_name: str,
    cur_dir_name: str,
    dir_list: List[str],
    file_list: List[Tuple[str, str, int]],
) -> None:
    entries_api: str = (
        "https://cloud.tsinghua.edu.cn/api/v2.1/share-links/"
        + f"{share_id}/dirents/?thumbnail_size=48&path={quote(cur_dir_name)}"
    )
    entry_list: List[dict] = json.loads(requests.get(entries_api).text)["dirent_list"]
    for entry_info in entry_list:
        if not entry_info["is_dir"]:
            remote_url: str = (
                "https://cloud.tsinghua.edu.cn/d/"
                + f"{share_id}/files/?p={quote(entry_info['file_path'])}&dl=1"
            )
            local_path: str = root_dir_name + entry_info["file_path"]
            size: int = entry_info["size"]
            ext = os.path.splitext(local_path)[1][1:]
            if ext not in exclude_ext_list:
                file_list.append((remote_url, local_path, size))
                size_sum = sum([size for _, _, size in file_list])
                print(f"\r共找到{len(file_list)}个满足条件的文件，总大小为{fs(size_sum)}。", end="")
        else:
            local_path: str = root_dir_name + entry_info["folder_path"]
            dir_list.append(local_path)
            search_entries(
                exclude_ext_list,
                share_id,
                root_dir_name,
                entry_info["folder_path"],
                dir_list,
                file_list,
            )


def download_entries(
    root_dir_name: str, dir_list: List[str], file_list: List[Tuple[str, str, int]]
) -> None:
    for local_path in dir_list:
        os.makedirs(local_path, exist_ok=True)
    size_sum = sum([size for _, _, size in file_list])
    dl_sum = 0
    with tqdm(total=size_sum, desc=root_dir_name, position=1) as bar:
        for index, (remote_url, local_path, size) in enumerate(file_list):
            dl_num = 0
            req = requests.get(remote_url, stream=True)
            with open(local_path, "wb") as file_output:
                with tqdm(total=size, desc=local_path, leave=False) as pbar:
                    for chunk in req.iter_content(512 * 1024):
                        dl_num += len(chunk)
                        dl_sum += len(chunk)
                        file_output.write(chunk)
                        pbar.update(len(chunk))
                        bar.update(len(chunk))
                        pbar.set_postfix_str(f"{fs(dl_num)}/{fs(size)}")
                        bar.set_postfix_str(f"{fs(dl_sum)}/{fs(size_sum)}")


@click.command()
@click.option(
    "--exclude-exts",
    default="",
    help="Comma-separated list of file extensions, e.g. mp4,mp3 .",
)
@click.argument("url", type=str)
def main(exclude_exts: str, url: str):
    """Recursively download files from the Tsinghua Cloud."""
    exclude_ext_list: List[str] = exclude_exts.split(",")

    share_id_start_idx: int = url.find("/d/") + 3
    share_id_end_idx: int = share_id_start_idx + 20
    share_id: str = url[share_id_start_idx:share_id_end_idx]

    root_dir_result = re.search(
        r"<meta property=\"og:title\" content=\"(.*?)\" />", requests.get(url).text
    )
    if root_dir_result is None:
        assert False
    root_dir_name: str = root_dir_result.group(1)

    dir_list: List[str] = [root_dir_name + "/"]
    file_list: List[Tuple[str, str, int]] = []

    search_entries(exclude_ext_list, share_id, root_dir_name, "/", dir_list, file_list)
    print()

    download_entries(root_dir_name, dir_list, file_list)


main()
