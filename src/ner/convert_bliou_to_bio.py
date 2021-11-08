

from io import FileIO
from typing import List

import argparse, sys


def convert_bliou_to_bio(input_files: List[str], output_file: str):
    out_file = open(output_file, "w")
    for file_path in input_files:
        f = open(file_path, "r")

        __convert_bliou_file_to_bio(f, out_file)

        f.close()
    
    out_file.close()

def __convert_bliou_file_to_bio(input_file: FileIO, out_file: FileIO):
    
    lines = input_file.readlines()
    previous_tag = ''
    for line in lines: 
        line_split = line.split('\t')
        if len(line_split) == 2:
            word = line_split[0].strip()
            tag = line_split[0]
            previous_tag = tag
            print (word + "\tO")
            out_file.write(word + "\tO" + "\n")
        elif len(line_split) == 3:
            word = line_split[0]
            tag = line_split[1]
            entity = line_split[2].strip()
            if tag == 'BEGIN' or tag == 'UNIT':
                print (word + "\tB-" + entity)
                out_file.write(word + "\tB-" + entity + "\n")
            elif tag == 'IN' or tag == 'LAST':  
                print (word + " I-" + entity)
                out_file.write(word + "\tI-" + entity + "\n")
        else: 
            print("")
            out_file.write("\n")


def init_argparse() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(
        usage="%(prog)s file/path1 file/path2 --out=output/file/path",
        description="Convert files into BIO format suitable for traning in Flair"
    )

    parser.add_argument('input', nargs="+", help='Input file in the BLIOU format')
    parser.add_argument('--out', required=True, help='output file in BIO format')

    return parser


if __name__ == "__main__":
    parser = init_argparse()


    args=parser.parse_args()

    input_files = args.input
    if len(input_files) > 0 and 'out' in args:
        convert_bliou_to_bio(input_files, args.out)
        