from typing import List

from tqdm import tqdm
import spacy
from spacy.tokens import DocBin
import json
import argparse

def get_examples_from_json(file_name):
    with open(file_name) as f:
        data = list(json.load(f))
    return data

def prepare_examples(files: List[str]) -> List:
    spacy_examples = []
    for file_path in files:
        file_data = get_examples_from_json(file_name=file_path)
        spacy_examples.extend(file_data)
    return spacy_examples


def transfer_to_binary(examples: list, model_path):
    nlp = spacy.blank("en") # load a new spacy model
    db = DocBin() # create a DocBin object

    TRAIN_DATA = examples
    for example in tqdm(TRAIN_DATA): # data in previous format
        doc = nlp.make_doc(example['text']) # create doc object from text
        ents = []
        for entity in example["entities"]: # add character indexes
            span = doc.char_span(entity['begin'], entity['end'], label=entity['label'], alignment_mode="contract")
            if span is None:
                print("Skipping entity")
            else:
                ents.append(span)
        doc.ents = ents # label the text with the ents
        db.add(doc)

    db.to_disk(model_path) # save the docbin object
    

def init_argparse() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(
        usage="%(prog)s file/path1 file/path2 --out=output/file/path",
        description="Convert files into BIO format suitable for traning in Flair"
    )

    parser.add_argument('input', nargs="+", help='Input file in JSON format')
    parser.add_argument('--out', required=True, help='output file SPACY binary format')

    return parser


if __name__ == "__main__":
    parser = init_argparse()


    args=parser.parse_args()

    input_files = args.input
    if len(input_files) > 0 and 'out' in args:
        examples = prepare_examples(input_files)
        transfer_to_binary(examples, args.out)