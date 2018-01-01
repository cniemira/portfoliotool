import argparse
import logging
import os

from portfoliotool.herolab.reader import PorReader
from portfoliotool.rptools.writer import RptokWriter


log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

argp = argparse.ArgumentParser(
    description="PortfolioTool"
    )

log_args = argp.add_mutually_exclusive_group()
argp.add_argument('POR_FILE', action='store',
                  type=argparse.FileType('rb'))


def main():
    args = argp.parse_args()
    portfolio = PorReader(args.POR_FILE)
    for character in portfolio.characters:
        token = RptokWriter(character)
        output_file = os.path.join(
            '/Users/siege/Desktop',
            character.name + '.rptok'
            )
        token.save_as(output_file)


if __name__ == '__main__':
    main()
