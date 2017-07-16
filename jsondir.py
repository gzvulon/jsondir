#!/usr/bin/env python
import os
import json
import logging
import argparse

_log = logging.getLogger('jsondir')
_cfg_json_dumps = dict(
    indent=4,
    sort_keys=True
)


def dir_to_json(json_path, dir_path, dry=False):
    items = os.listdir(dir_path)
    logging.debug("found={}".format(items))

    root = {}
    for item in items:
        item_path = os.path.join(dir_path, item)
        logging.debug("process='{}'".format(item_path))
        if os.path.isfile(item_path):
            with open(item_path) as fd:
                content = fd.read()
            filename = os.path.basename(item)
            root[filename] = content
            logging.debug("add='{}'".format(filename))
        else:
            logging.info("skip='{}'".format(item_path))
    js_data = json.dumps(root, **_cfg_json_dumps)
    if not dry:
        with open(json_path, 'w') as wd:
            wd.write(js_data)
    return root


def json_to_dir(json_path, dir_path, dry=False):
    with open(json_path, 'r') as rd:
        js_data = rd.read()
    root = json.loads(js_data)
    logging.debug("found='{}'".format(root.keys()))

    if not dry:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            logging.debug("created='{}'".format(dir_path))

    for item, content in root.items():
        logging.debug("process='{}'".format(item))
        dest_path = "{dir_path}/{item}".format(dir_path=dir_path, item=item)
        if not dry:
            with open(dest_path, 'w') as wd:
                wd.write(content)
    return root


def _default_dest(json_path=None, dir_path=None):
    if json_path:
        return os.path.basename(json_path)
    if dir_path:
        return "{}.{}".format(dir_path, 'dir.json')


def _get_cli_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("src", help='json or dir to transform')
    parser.add_argument("--dest", default=None, required=False,
                        help='destination path')
    parser.add_argument("--dry", action='store_true',
                        help='dry run')
    return parser


def run_cli(args):
    src = args.src
    if not os.path.exists(src):
        raise Exception('Cannot find {}'.format(src))
    elif os.path.isfile(src):
        action = json_to_dir
        json_path = src
        dir_path = args.dest or _default_dest(json_path=json_path)
        dest = dir_path
    elif os.path.isdir(src):
        action = dir_to_json
        dir_path = src
        json_path = args.dest or _default_dest(dir_path=dir_path)
        dest = json_path
    else:
        raise Exception('{} should be json or dir')
    pack_info = action(json_path=json_path, dir_path=dir_path, dry=args.dry)
    result = dict(_meta=dict(kind='pack_info', pwd=os.getcwd()),
                  data=dict(info=pack_info, dest=dest))
    return result


def _setup_logging():
    logging.basicConfig(level=logging.DEBUG)


if __name__ == '__main__':
    _setup_logging()
    parser = _get_cli_parser()
    args = parser.parse_args()
    result = run_cli(args)
    logging.info(json.dumps(result, **_cfg_json_dumps))
