from flair.data import Corpus
from flair.datasets import ColumnCorpus
from flair.embeddings import TokenEmbeddings, WordEmbeddings, StackedEmbeddings,FlairEmbeddings, TransformerWordEmbeddings
from typing import List

from flair.models import SequenceTagger
from flair.trainers import ModelTrainer

import torch
from torch.optim.lr_scheduler import OneCycleLR
import yaml


def train_ner():
    # define columns
    columns = {0 : 'text', 1 : 'ner'}# directory where the data resides
    data_folder = 'data/annotation'# initializing the corpus
    corpus: Corpus = ColumnCorpus(data_folder, columns,
                                train_file = 'annotation-result-BIO.txt',
                                test_file = 'annotation-result-BIO-val.txt',
                                dev_file = 'annotation-result-BIO-val.txt')

    print(len(corpus.train))
    print(corpus.train[0].to_tagged_string())

    # tag to predict
    tag_type = 'ner'# make tag dictionary from the corpus
    tag_dictionary = corpus.make_tag_dictionary(tag_type=tag_type)
    print(tag_dictionary)


    # embedding_types : List[TokenEmbeddings] = [
    #         #WordEmbeddings('glove'),
    #         WordEmbeddings('crawl')
    #         ## other embeddings
    #         ]
    # embeddings : StackedEmbeddings = StackedEmbeddings( embeddings=embedding_types)

    embeddings = StackedEmbeddings([
                                    WordEmbeddings('crawl'),
                                    FlairEmbeddings('models/jobs_lm_forward/best-lm.pt'),
                                    FlairEmbeddings('models/jobs_lm_backward/best-lm.pt'),
                                ])


    tagger: SequenceTagger = SequenceTagger(hidden_size=256,
                                            embeddings=embeddings,
                                            tag_dictionary=tag_dictionary,
                                            tag_type=tag_type,
                                            use_crf=True)
    print(tagger)   



    trainer: ModelTrainer = ModelTrainer(tagger, corpus)

    # 7. start training
    trainer.train('models/flair-skills-ner',
                learning_rate=0.1,
                mini_batch_size=64,
                max_epochs=150)

def train_ner_bert(epochs: int, use_crf: bool, use_rnn: bool):
    # define columns
    columns = {0 : 'text', 1 : 'ner'}# directory where the data resides
    data_folder = 'data/annotation'# initializing the corpus
    corpus: Corpus = ColumnCorpus(data_folder, columns,
                                train_file = 'annotation-result-BIO.txt',
                                test_file = 'annotation-result-BIO-val.txt',
                                dev_file = 'annotation-result-BIO-val.txt')

    print(len(corpus.train))
    print(corpus.train[0].to_tagged_string())

    # 2. what label do we want to predict?
    label_type = 'ner'

    # 3. make the label dictionary from the corpus
    label_dict = corpus.make_label_dictionary(label_type=label_type)
    label_dict.add_unk = True
    print(label_dict)

    # 4. initialize fine-tuneable transformer embeddings WITH document context
    embeddings = TransformerWordEmbeddings(
        model='roberta-base',
        layers="-1",
        subtoken_pooling="first",
        fine_tune=True,
        use_context=True,
    )

    # 5. initialize bare-bones sequence tagger (no CRF, no RNN, no reprojection)
    tagger = SequenceTagger(
        hidden_size=256,
        embeddings=embeddings,
        tag_dictionary=label_dict,
        tag_type='ner',
        use_crf=use_crf,
        use_rnn=use_rnn,
        reproject_embeddings=False,
    )

    # 6. initialize trainer with AdamW optimizer
    trainer = ModelTrainer(tagger, corpus)

    # 7. run training with XLM parameters (20 epochs, small LR, one-cycle learning rate scheduling)
    trainer.fine_tune('models/flair-ner-bert',
                learning_rate=5.0e-6,
                mini_batch_size=4,
                mini_batch_chunk_size=2,  # remove this parameter to speed up computation if you have a big GPU
                max_epochs=epochs,  # 10 is also good
                # scheduler=OneCycleLR,
                # embeddings_storage_mode='none',
                # weight_decay=0.,
                )
                    

if __name__ == "__main__":
    params = yaml.safe_load(open('params.yaml'))['flair']['ner_train']

    train_ner_bert(epochs=params['num_epochs'], 
                   use_crf=params['crf'],
                   use_rnn=params['rnn']);

