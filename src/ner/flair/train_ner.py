from flair.data import Corpus
from flair.datasets import ColumnCorpus
from flair.embeddings import TokenEmbeddings, WordEmbeddings, StackedEmbeddings,FlairEmbeddings
from typing import List

from flair.models import SequenceTagger
from flair.trainers import ModelTrainer


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

if __name__ == "__main__":
    train_ner()

