from pathlib import Path
from flair.data import Sentence
from flair.models import SequenceTagger
from flair.tokenization import SegtokSentenceSplitter

from entity_dto import EntityDto
from text_preparateion_service import TextPreparationService
from typing import List


class FlairSkillsExtractionService: 

    model = None

    def __init__(self, model_path: Path, textCleaningService: TextPreparationService):
        self.model = SequenceTagger.load(model_path)

    def predict(self, text) -> List[EntityDto]:
        # initialize sentence splitter
        splitter = SegtokSentenceSplitter()
        # use splitter to split text into list of sentences
        sentences = splitter.split(text)

        self.model.predict(sentences)
        
        entities = []
        for sentence in sentences:
            for entity in sentence.get_spans('ner'):
                for label in entity.labels: 
                    # print(label.value + " score " + str(label.score))
                    entities.append(EntityDto(text=entity.text, label=label.value))
        
        return entities


def get_flair_skills_extraction_service(model_path: Path)  -> FlairSkillsExtractionService :
    return FlairSkillsExtractionService(model_path, TextPreparationService())

