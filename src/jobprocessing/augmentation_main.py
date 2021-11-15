from skills_aug_pipeline import create_skills_extr_pipeline
from flair_skills_extraction_service import FlairSkillsExtractionService, get_flair_skills_extraction_service
from utils import common_parameters

from typing import Dict, List, Optional
from sqlalchemy.orm import sessionmaker
from seek_db_model import create_table, db_connect




def create_flair_extraction_service(conf) -> FlairSkillsExtractionService:
    return get_flair_skills_extraction_service(conf['flair']['ner_model'])

if __name__ == "__main__":
    config = common_parameters()

    engine = db_connect()
    create_table(engine)
    session_maker = sessionmaker(bind=engine)
   
    flair_extr_serv = create_flair_extraction_service(config)
    skills_aug_pipeline = create_skills_extr_pipeline(session_maker, flair_extr_serv)
    skills_aug_pipeline.process_vacancies()
    
    session_maker.close()
    engine.dispose()