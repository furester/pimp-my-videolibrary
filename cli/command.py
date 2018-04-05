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

    cfg = {}
    with open(".config.yml", 'r') as ymlfile:
        try:
            cfg = yaml.load(ymlfile)
        except yaml.YAMLError as exc:
            print(exc)

    storage = pimp.storage.Storage()
    ut = pimp.utility.Utility(True)

    retriever = pimp.retriever.Retriever(cfg['start_path'], cfg['extensions'], storage)
    if args.use_fresh_retriver:
        retriever.cacheEnabled(False)

    file_list = retriever.retrieveFileList(args.use_cache_retriver)

    for f in file_list:
        a = storage.retrieveMovieMetadata(f)
        if a is not None:
            ut.log(a)

    # TODO debug version, optimize it!
    f_name_match = f_to_move = set()
    for f in file_list:
        start_check = False
        ut.log("---> Init")
        ut.log(f)
        if f in f_name_match:
            ut.log("### SKIP")
            continue
        # initialize parser
        main_parser = pimp.parser.Parser(f)
        for f2 in file_list:
            if f == f2:
                start_check = True
                continue
            # ordered list: only after found same string start to analyze
            if not start_check:
                continue
            # compare file name: https://en.wikipedia.org/wiki/Levenshtein_distance
            _x = main_parser.normalized_levenshtein(f2)
            # if similar at cfg['lev_threshold']%
            if _x < float(cfg['lev_threshold']):
                continue

            f_name_match.add(f2)
            ut.log("Matching file: ", f, f2, _x)
            # extract metadata
            main_parser.extractInfo()
            # initialize second parser
            second_parser = pimp.parser.Parser(f2)
            second_parser.extractInfo()
            # compare
            if main_parser.compare(second_parser) > 0:
                f_to_move.add(f2)
                ut.log("Move!!! ", f2)
                ut.log("M ", main_parser.getInfo())
                ut.log("S ", second_parser.getInfo())
                ut.log("!!!")
        ut.log("End  <---")


if __name__ == '__main__':
    main()
