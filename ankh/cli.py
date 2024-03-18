import ankh
import argparse
from itertools import zip_longest


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "template",
        help="Template files to load. Defaults to ankh.template",
        nargs="+",
    )

    parser.add_argument(
        "-o",
        "--output",
        help="File to save the parsed template and feeds to. Defaults to input.html",
        nargs="*",
        default=[],
    )

    parser.add_argument(
        "-v",
        "--verbose",
        dest="verbose",
        help="Be verbose about what is going on",
        action="store_true",
        default=False,
    )

    parser.add_argument(
        "-c",
        "--cache",
        dest="cache",
        help="Cache feeds",
        action="store_true",
        default=False,
    )

    parser.add_argument(
        "--cache_path",
        dest="cache_path",
        help="The directory to store cache files",
        default="./ankh_cache",
    )

    parser.add_argument(
        "-t",
        "--template-paths",
        dest="template_paths",
        help="Additional template path, separated by comma",
        default=None,
    )

    options = parser.parse_args()

    if options.template_paths is None:
        options.template_paths = []
    else:
        options.template_paths = options.template_paths.split(",")

    print(options.template, options.output)

    for template, outfile in zip_longest(
        options.template, options.output, fillvalue="?"
    ):
        if outfile == "?":
            outfile = f"{template}.html"

        ankh.parse(template, outfile, options)
