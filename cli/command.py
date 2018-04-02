# -*- coding: utf-8 -*-

import shutil
import sys
import argparse
import yaml
import os
from . import _program
from clint.textui import puts, indent, colored
import pimp


def main(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(prog=_program)

    parser.add_argument("--cache",
                        help="Specify a flag",
                        action="store_true")

    # Allow --use-cache-retriver and --use-fresh-retriver options, but not together.
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--use_cache_retriver",
                       help="Use cache for retriever component - if present",
                       action="store_true")
    group.add_argument("--use_fresh_retriver",
                       help="Don't use cache for retriever component",
                       action="store_true")

    args = parser.parse_args(args)

    if not os.path.isfile(".config.yml"):
        print("configuration file needed, creating one from template")
        shutil.copyfile("config.yml.template", ".config.yml")

    with open(".config.yml", 'r') as ymlfile:
        try:
            cfg = yaml.load(ymlfile)
        except yaml.YAMLError as exc:
            print(exc)

    storage = pimp.storage.Storage()

    retriever = pimp.retriever.Retriever(cfg['start_path'], cfg['extensions'], storage)
    if args.use_fresh_retriver:
        retriever.setCacheEnabled(False)

    file_list = retriever.retrieveFileList(force_cache = args.use_cache_retriver)

    for f in file_list:
        try:
            # initialize parser
            main_parser = pimp.parser.Parser(f)
        except TypeError as exc:
            print("TypeError: {} for {}".format(exc, f))
            continue
        except Exception as err:
            print("Generic Exception: {} for {}".format(exc, f))
            continue

        try:
            # extract metadata
            main_parser.extractInfo()
        except TypeError as exc:
            print("TypeError on extract: {} for {}".format(exc, f))
            continue

        storage.storeMovieMetadata(f, main_parser._file_data)

    for f in file_list:
        a = storage.retrieveMetadata(f)
        print(a)

    # TODO debug version, optimize it!
    for f in file_list:
        start_check = False
        print "---> Init"
        print f
        # initialize parser
        main_parser = pimp.parser.Parser(f)
        for f2 in file_list:
            if f == f2:
                start_check = True
                continue
            # ordered list: only after found same string start to analize
            if not start_check:
                continue
            # compare file name: https://en.wikipedia.org/wiki/Levenshtein_distance
            _x = main_parser.normalized_levenshtein(f2)
            # if similar at cfg['lev_threshold']%
            if _x < float(cfg['lev_threshold']):
                continue
            print "Matching file: ", f, f2, _x
            # extract metadata
            main_parser.extractInfo()
            # initialize second parser
            second_parser = pimp.parser.Parser(f2)
            second_parser.extractInfo()
            # match
            if main_parser.match(second_parser):
                # TODO rewrite it or in this way it check the files twice
                print "Match!!! ", f2
                print "M ", main_parser._file_data
                print "S ", second_parser._file_data
                print "!!!"
        print "End  <---"


if __name__ == '__main__':
    main()
