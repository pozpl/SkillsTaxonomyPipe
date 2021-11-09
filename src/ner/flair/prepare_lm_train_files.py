from io import FileIO
from typing import List

import argparse
import sqlite3
import math
import os
import yaml


def get_num_of_vacacnies(c):
    c.execute('SELECT COUNT(*) FROM vacancy')
    data = c.fetchall()
    return data[0][0]
   
def read_vacancy_db_chunk(c, offset, limit, file_path):
    query = 'SELECT * FROM vacancy LIMIT ? offset ?'
    c.execute(query, [limit, offset])
    data = c.fetchall()
    #print(data)
    f = open(file_path, "w")
    for row in data:
        text = row[1] + "\n " + row[2]
        cleared_text=text.encode('ascii','ignore').decode("utf-8")
        f.write(cleared_text)
    f.close()        

def prepare_language_model_train_set(database_file_path, output_path):
    conn = sqlite3.connect(database_file_path)
    c = conn.cursor()
    
    num_of_vac = get_num_of_vacacnies(c)
    print(num_of_vac)
    chunk_size = math.floor(num_of_vac/100)
    print(chunk_size)
    for chk_id in range(0,100):
        offset = chk_id * chunk_size
        file_path = os.path.join(output_path, 'train_split_' + str(chk_id))
        read_vacancy_db_chunk(c, offset, chunk_size, file_path)



def init_argparse() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(
        usage="%(prog)s jobs/database/file/path",
        description="Get text from jobs database and convert them to Flair Language model training set"
    )

    parser.add_argument('input', help='SQLite database with jobs')

    return parser


if __name__ == "__main__":
    parser = init_argparse()
    
    args=parser.parse_args()

    params = yaml.safe_load(open('params.yaml'))['flair']['language_model_train']

    train_set_path = os.path.join(params['corpus_dir'], 'train')
    is_exist = os.path.exists(train_set_path)
    if not is_exist:
        os.makedirs(train_set_path)

    database_file = args.input
    prepare_language_model_train_set(database_file, train_set_path)