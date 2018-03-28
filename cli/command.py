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

    parser.add_argument("--square",
                        help="Used for testing",
                        type=int,
                        default=None)

    parser.add_argument("--int_value",
                        help="display a square of a given number",
                        type=int)

    parser.add_argument("--float_value",
                        help="display a square of a given number",
                        type=int)

    parser.add_argument("-f",
                        "--flag",
                        help="Specify a flag",
                        action="store_true")
    parser.add_argument("--rating",
                        help="An option with a limited range of values",
                        choices=[1, 2, 3],
                        type=int)

    # Allow --day and --night options, but not together.
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--day",
                       help="mutually exclusive option",
                       action="store_true")
    group.add_argument("--night",
                       help="mutually exclusive option",
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

    # "/volume1/video/film/"
    l = pimp.retrieve.print_filelist(cfg['start_path'], cfg['extensions'])
    print(l)
    # TODO debug version, optimize it!
    for f in l:
        print "---> Init"
        print f
        # initialize parser
        main_parser = pimp.parser.Parser(f)
        for f2 in l:
            if f == f2:
                continue
            # compare file name: https://en.wikipedia.org/wiki/Levenshtein_distance
            _x = main_parser.levenshtein(f2)
            # if similar
            if _x > 15:
                continue
            print(f, f2, _x)
            # extract metadata
            main_parser.extractInfo()
            # initialize second parser
            second_parser = pimp.parser.Parser(f2)
            second_parser.extractInfo()
            # match
            if main_parser.match(second_parser):
                # TODO rewrite it or in this way it check the files twice
                print "Match!!!"
                print main_parser._file_data
                print second_parser._file_data
                print "!!!"
        print "End  <---"

    if args.square:
        print(args.square ** 2)
    else:
        with indent(4):
            puts(colored.blue("Arguments"))
            puts(colored.green("int value: ") + str(args.int_value))
            puts(colored.green("float value: ") + str(args.float_value))
            puts(colored.green("flag: ") + str(args.flag))
            puts(colored.green("rating: ") + str(args.rating))


if __name__ == '__main__':
    main()
