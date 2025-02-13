import os
from typing import List, Dict, Optional
import cohere
from pydantic import BaseModel
import json


class Prompts:
    CREATE_CARDS_N = """
    You are an expert tutor. Given all of this material, I want you to create {} "flashcards" for the concepts in these documents. 
    A flashcard is defined as a pair of concept -> description mapping with an ID. Keep the descriptions concise yet with sufficient detail. 
    Make sure each flashcard is self-contained, it should make sense if I pick it up on its own. References to other parts of the content that don't make sense without context are not suitable for flashcard-style learning.
    All information in the flashcards MUST come from the provided content enclosed in <content></content> tags.
    Return an array of objects in JSON format, with each object having with the keys "id", "concept", "description".
    
    <content>
    {}
    </content>
    """
    CREATE_CARDS_AUTO = """
    You are an expert tutor. Given all of this material, I want you to create "flashcards" for the concepts in these documents. 
    A flashcard is defined as a pair of concept -> description mapping with an ID. Keep the descriptions concise yet with sufficient detail. 
    Create as many flashcards as needed to cover all of the material. Do not miss anything. It is better to include an extra flashcard than not to if you are unsure.
    Make sure each flashcard is self-contained, it should make sense if I pick it up on its own. References to other parts of the content that don't make sense without context are not suitable for flashcard-style learning.
    All information in the flashcards MUST come from the provided content enclosed in <content></content> tags.
    Return an array of objects in JSON format, with each object having with the keys "id", "concept", "description".
    
    <content>
    {}
    </content>
    """
    # You are an expert tutor. Given all of this material, I want you to create 40 "flashcards" for the concepts in these documents. All information in the flashcards MUST come from the provided content enclosed in <content></content> tags. A flashcard is defined as a pair of concept -> description mapping with an ID. Keep the descriptions concise yet with sufficient detail. Return in JSON format with the keys "id", "concept", "description".


class Card(BaseModel):
    id: int
    concept: str
    description: str


class LLMCardCreator:
    def __init__(self):
        self.cohere_client = cohere.ClientV2(api_key=os.getenv("COHERE_API_KEY"))

    def _keyword_deduplicate_file_content(self, text: str) -> str:
        return text

    def _semantic_deduplicate_file_content(self, text: str) -> str:
        return text

    def create_cards(
        self,
        text: str,
        n_cards: Optional[int] = None,
        model: str = "command-r-plus-08-2024",
    ) -> List[Dict[str, str]]:
        text = self._keyword_deduplicate_file_content(text)
        text = self._semantic_deduplicate_file_content(text)

        response = self.cohere_client.chat(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": (
                        Prompts.CREATE_CARDS_AUTO.format(text)
                        if not n_cards
                        else Prompts.CREATE_CARDS_N.format(n_cards, text)
                    ),
                }
            ],
        )

        raw_cards = response.message.content[0].text
        cards_data = json.loads(raw_cards)

        cards = [Card.model_validate(card) for card in cards_data]

        return cards


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    with open("../mock_data/ppt-to-md.md") as f:
        example_content = f.read()

    card_creator = LLMCardCreator()
    cards = card_creator.create_cards(text=example_content, n_cards=None)

    for card in cards:
        print(card)
