"""
Picacomic Command Line Interface 命令行接口
"""
import sys
import os
import argparse


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Picacomic Comic Downloader')
    subparsers = parser.add_subparsers(title='commands', dest='command')

    # 搜索命令
    search_parser = subparsers.add_parser('search', help='搜索漫画')
    search_parser.add_argument('keyword', help='搜索关键词')
    search_parser.add_argument('-p', '--page', type=int, default=1, help='页码')
    search_parser.add_argument('-o', '--option', help='配置文件路径')

    # 下载命令
    download_parser = subparsers.add_parser('download', help='下载漫画')
    download_parser.add_argument('comic_id', help='漫画ID')
    download_parser.add_argument('-o', '--option', help='配置文件路径')

    args = parser.parse_args()

    if args.command == 'search':
        from picacomic import search_comics, create_option
        option = None
        if args.option:
            option = create_option(args.option)
        result = search_comics(args.keyword, page=args.page, option=option)
        print(f'搜索到 {result["total"]} 本漫画')
        for i, comic in enumerate(result['results'], 1):
            print(f'[{i}] {comic["title"]} (ID: {comic["comic_id"]})')
    elif args.command == 'download':
        from picacomic import download_album, create_option
        option = None
        if args.option:
            option = create_option(args.option)
        print(f'开始下载漫画: {args.comic_id}')
        download_album(args.comic_id, option=option)
        print('下载完成')
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
