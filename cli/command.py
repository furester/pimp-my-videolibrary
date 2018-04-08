# -*- coding: utf-8 -*-

import shutil
import sys
import argparse
import yaml
import os
import time
import datetime
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
    ut = pimp.utility.Utility(False)

    retriever = pimp.retriever.Retriever(cfg['start_path'], cfg['extensions'], storage)
    if args.use_fresh_retriver:
        retriever.cacheEnabled(False)

    file_list = retriever.retrieveFileList(args.use_cache_retriver)

    # TODO debug version, optimize it!
    start_time = time.time()
    _count = 0
    _len = len(file_list)
    f_name_match = set()
    f_to_move = {}
    for f in file_list:
        start_check = False
        _count += 1
        ut.out("---> Init {:4d}/{:4d} {:3.2f}% {}"
               .format(_count, _len, round((float(_count) / _len) * 100, 2),
                       str(datetime.timedelta(seconds=(time.time() - start_time)))))
        ut.log(f)
        if f in f_name_match:
            ut.log("### SKIP")
            continue
        # initialize parser
        _md = storage.retrieveMovieMetadata(f)
        if _md is not None:
            main_parser = pimp.parser.Parser(f, _md)
        else:
            ut.log("### ERROR")
            continue
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
            _d = main_parser.levenshtein(f2, f, False)
            if _d == 1 and len(f2) == len(f):
                _diff = ''
                for i in range(len(f)):
                    letter1 = f[i:i + 1]
                    letter2 = f2[i:i + 1]
                    # create string with differences
                    if letter1 != letter2:
                        _diff += letter1
                # _diff = set.intersection(set(f2), set(f))
                ut.log("Diff: {}".format(_diff))
                try:
                    if 0 < int(_diff) < 4:
                        continue
                except ValueError:
                    aa = None
            f_name_match.add(f2)
            ut.log("Matching file: {}".format(_x))
            ut.log(f)
            ut.log(f2)
            # extract metadata
            main_parser.extractInfo()
            # initialize second parser
            _md2 = storage.retrieveMovieMetadata(f2)
            if _md2 is not None:
                second_parser = pimp.parser.Parser(f2, _md2)
            else:
                second_parser = pimp.parser.Parser(f2)
                second_parser.extractInfo()
            # compare
            if main_parser.compare(second_parser) > -1:
                fb = f #os.path.basename(f)
                f2b = f2 #os.path.basename(f2)
                if fb in f_to_move:
                    f_to_move[fb].append(f2b)
                else:
                    f_to_move[fb] = [f2b]
                ut.log("Move!!! {}".format(f2))
                ut.log("M {}".format(main_parser.getInfo()))
                ut.log("S {}".format(second_parser.getInfo()))
                ut.log("!!!")
        ut.log("End  <---")

    ut.out("FILE(s) TO MOVE")
    ut.out("===============")

    for key in f_to_move.keys():
        ut.out("{}".format(key.replace(cfg['start_path'], '')))
        for to_move in f_to_move[key]:
            ut.out(" {}".format(to_move.replace(cfg['start_path'], '')))
        ut.out(".")


if __name__ == '__main__':
    main()
