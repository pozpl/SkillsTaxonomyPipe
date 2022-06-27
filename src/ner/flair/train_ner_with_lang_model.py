from select import epoll
from flair.data import Corpus
from flair.datasets import ColumnCorpus
from flair.embeddings import TokenEmbeddings, WordEmbeddings, StackedEmbeddings,FlairEmbeddings, TransformerWordEmbeddings
from typing import List

from flair.models import SequenceTagger
from flair.trainers import ModelTrainer

import torch
from torch.optim.lr_scheduler import OneCycleLR
import yaml


def train_ner_with_lm(epochs: int = 150, use_crf: bool = True):
    # define columns
    columns = {0 : 'text', 1 : 'ner'}# directory where the data resides
    data_folder = 'data/annotation'# initializing the corpus
    corpus: Corpus = ColumnCorpus(data_folder, columns,
                                train_file = 'annotation-result-BIO.txt',
                                test_file = 'annotation-result-BIO-val.txt',
                                dev_file = 'annotation-result-BIO-val.txt')

    
    # tag to predict
    label_type = 'ner'# make tag dictionary from the corpus
    tag_dictionary = corpus.make_label_dictionary(label_type=label_type)
    

    # embedding_types : List[TokenEmbeddings] = [
    #         #WordEmbeddings('glove'),
    #         WordEmbeddings('crawl')
    #         ## other embeddings
    #         ]
    # embeddings : StackedEmbeddings = StackedEmbeddings( embeddings=embedding_types)

    embeddings = StackedEmbeddings([
                                    WordEmbeddings('glove'),
                                    FlairEmbeddings('models/jobs_lm_forward/best-lm.pt'),
                                    FlairEmbeddings('models/jobs_lm_backward/best-lm.pt'),
                                ])


    tagger: SequenceTagger = SequenceTagger(hidden_size=256,
                                            embeddings=embeddings,
                                            tag_dictionary=tag_dictionary,
                                            tag_type=label_type,
                                            use_crf=use_crf) 



    trainer: ModelTrainer = ModelTrainer(tagger, corpus)

    # 7. start training
    trainer.train('models/flair-ner-lm',
                learning_rate=0.1,
                mini_batch_size=32,
                mini_batch_chunk_size=1,  # remove this parameter to speed up computation if you have a big GPU
                max_epochs=epochs)

                    

if __name__ == "__main__":
    
    train_ner_with_lm();

