from entity_dto import EntityDto
from seek_db_model import Skill, Vacancy, create_table, db_connect
from flair_skills_extraction_service import FlairSkillsExtractionService
from tqdm import tqdm

class SkillsAugmentationPipeline(object):

    def __init__(self, session_maker, flair_skills_extraction_service: FlairSkillsExtractionService):

        self.session_maker = session_maker
        self.flair_skills_extraction_service = flair_skills_extraction_service

        self.skills_cache = {}

    def process_vacancies(self):
        """Save deals in the database.

        This method is called for every item pipeline component.
        """
        session = self.session_maker()

        # get all unprocessed vacacnies
        unprocessed_count = self.count_unprocessed_vacacnies(session)
        print("Unprocessed text: " + str(unprocessed_count))
        batch_size = 1000
        for i in tqdm(range(0,unprocessed_count, batch_size)):
            unprocessed_vacacnies = self.get_unprocessed_vacacnies(session, batch_size)
        
            for vacancy in tqdm(unprocessed_vacacnies):
                # print(vacancy.title)

                skill_names = set()

                
                flair_extracted_skills = self.flair_skills_extraction_service.predict(vacancy.title + ' ' + vacancy.description)
                if len(flair_extracted_skills) == 0:
                    flair_extracted_skills.append(EntityDto(text='N/A', label='SKILL'))
                # print("=======Flair============")                
                for skill in flair_extracted_skills: 
                    # print ('Flair srkill: ' + skill.text)
                    skill_names.add(skill.text)
                try:
                    for skill_name in skill_names: 
                        skill = self.get_or_create_skill(session, skill_name)
                        vacancy.skills.append(skill)
                except:
                    session.rollback()
                    raise
            session.commit()
        




    @staticmethod
    def get_unprocessed_vacacnies(session, limit):
        vac_q = session.query(Vacancy).outerjoin(Skill, Vacancy.skills).filter(Skill.id == None).order_by(Vacancy.id).limit(limit)
        #print(vac_q)
        vacancies = vac_q.all()
    
        return vacancies

    @staticmethod
    def count_unprocessed_vacacnies(session):
        vac_q = session.query(Vacancy).outerjoin(Skill, Vacancy.skills).filter(Skill.id == None)
        #print(vac_q)
        vacancies = vac_q.count()
    
        return vacancies    

    def get_or_create_skill(self, session, skill_name: str) -> Skill:
        if skill_name in self.skills_cache:
            return self.skills_cache[skill_name]
        skill_to_return = session.query(Skill).filter(Skill.title == skill_name).first()
        
        if skill_to_return is None:
            skill_to_return = self.create_skill(session, skill_name)
        else:
            self.skills_cache[skill_name] = skill_to_return # only add skill from database to the cache
            
        return skill_to_return

    def create_skill(self, session, skill_name: str) -> Skill: 
        skill = Skill()
        skill.title = skill_name
        # try:
        #     session.add(skill)
        #     session.commit()
        # except:
        #     session.rollback()
        #     raise
        return skill
    

def create_skills_extr_pipeline(session_maker, flair_extr_service: FlairSkillsExtractionService):
    return SkillsAugmentationPipeline(session_maker, flair_extr_service)
    
