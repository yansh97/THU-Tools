# THU-Tools

## thu-cloud-dl.py

方便地递归下载清华云盘的方式，纯命令行环境执行，需要预先安装 `click`、`tqdm`、`requests` 包。目前为单进程下载，除非有大量小文件，否则效率还可以。

使用方式：
```
>>> python thu-cloud-dl.py --help
Usage: thu-cloud-dl.py [OPTIONS] URL

  Recursively download files from the Tsinghua Cloud.

Options:
  --exclude-exts TEXT  Comma-separated list of file extensions, e.g. mp4,mp3 .
  --help               Show this message and exit.

>>> python thu-cloud-dl.py --exclude-exts dmg,exe,gz https://cloud.tsinghua.edu.cn/d/xxxxxxxxxxxxxxxxxxxx/
共找到xx个满足条件的文件，总大小为xx.xxGB。
根目录/子目录/.../.../文件名:  45%|██████████▊             | 99090432/219518163 [00:20<00:19, 6201313.84it/s, 94.50MB/209.35MB]
根目录:   3%|█▎                                          | 100395635/3604065554 [00:22<09:25, 6200230.79it/s, 95.74MB/3.36GB]
```
