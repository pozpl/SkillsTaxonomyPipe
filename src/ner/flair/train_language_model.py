from flair.data import Dictionary
from flair.embeddings import FlairEmbeddings
from flair.trainers.language_model_trainer import LanguageModelTrainer, TextCorpus

from io import FileIO
from typing import List

import argparse
import os
import yaml



def train_language_model(train_corpus_path: str, is_forward: bool, model_path: str, n_iter: int) -> None: 
    # instantiate an existing LM, such as one from the FlairEmbeddings
    language_model = FlairEmbeddings('news-forward').lm if is_forward else FlairEmbeddings('news-backward').lm
    
    # are you fine-tuning a forward or backward LM?
    is_forward_lm = language_model.is_forward_lm

    print("Pretraining on forward LM: " + str(is_forward_lm))

    # get the dictionary from the existing language model
    dictionary: Dictionary = language_model.dictionary
    dictionary.add_unk = True

    # get your corpus, process forward and at the character level
    corpus = TextCorpus(train_corpus_path,
                        dictionary,
                        is_forward_lm,
                        character_level=True)

    # use the model trainer to fine-tune this model on your corpus
    trainer = LanguageModelTrainer(language_model, corpus)

    trainer.train(model_path,
                sequence_length=100,
                mini_batch_size=200,
                learning_rate=20,
                patience=10,
                max_epochs=n_iter,
                checkpoint=True)


def init_argparse() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(
        usage="%(prog)s --train_set=data/corpus --out=models/taggers/seek_lm_backward --is_forward=false",
        description="Convert files into BIO format suitable for traning in Flair"
    )

    parser.add_argument('--train_set', required=False, help='Path to train set text corpus')
    parser.add_argument('--out', required=False, help='path for output model')
    parser.add_argument('--num_epochs',type=int, required=False, help='Number of epochs to train model')
    parser.add_argument('--forward', dest='is_forward', action='store_true')
    parser.add_argument('--backward', dest='is_forward', action='store_false')
    parser.set_defaults(is_forward=True)

    return parser


if __name__ == "__main__":
    parser = init_argparse()


    args=parser.parse_args()

    is_exist = os.path.exists(args.out)
    if not is_exist:
        os.makedirs(args.out)

    params = yaml.safe_load(open('params.yaml'))['flair']['language_model_train']

    train_corpus= args.train_set if args.train_set != None else params['corpus_dir']
    n_iter=params['num_epochs']
    
    print("Train language model on corpus " + train_corpus)
    print("With output model path " + args.out)
    print("Direction forward: " + str(args.is_forward))
    

    train_language_model(train_corpus, args.is_forward, args.out, n_iter)
