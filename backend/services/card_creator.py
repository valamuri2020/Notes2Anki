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
    You are an expert tutor preparing study materials. Given this material, create flashcards designed to help students learn the *key concepts*. 
    Focus on the fundamental ideas, principles, and topics that students need to understand to master the subject.
    It excludes administrative details, logistical information, course outlines, introductory remarks, summaries, or meta-discussions about the content itself.

    Here are examples of the *types* of information that should NOT be included in flashcards:

    *   Course mechanics (website links, office hours)
    *   Course outlines (lists of topics)
    *   Administrative details (grading policies, late submission rules)
    *   Introductory or concluding remarks
    *   Meta-discussions about the content (e.g., "This topic is important because...")
    *   Anything not directly part of the core subject matter.

    Create a *complete* set of flashcards that covers *all* the material. Ensure *every* distinct concept, idea, principle, and topic mentioned in the content is represented by at least one flashcard. Do not omit any information. Err on the side of creating more flashcards rather than fewer.
    Prioritize granularity. Do not omit any information. It's better to have too many specific flashcards than a few overly general ones.

    A flashcard is defined as a pair of concept -> description mapping with an ID. Try not to repeat "concept" keys. Keep the descriptions concise yet with sufficient detail. 
    
    Do not miss any *key concepts*. It is better to include an extra flashcard if you are unsure.

    Make sure each flashcard is self-contained, it should make sense if I pick it up on its own. References to other parts of the content that don't make sense without context are not suitable for flashcard-style learning. 
    
    All information in the flashcards MUST come from the provided content enclosed in <content></content> tags. This is absolutely imperative and please do no hallucinate!

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

        print(f"Creating {'auto' if not n_cards else n_cards} cards with LLM")
        prompt = (
            Prompts.CREATE_CARDS_AUTO.format(text)
            if not n_cards
            else Prompts.CREATE_CARDS_N.format(n_cards, text)
        )

        response = self.cohere_client.chat(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": (prompt),
                }
            ],
        )

        raw_cards = response.message.content[0].text
        print(raw_cards)
        cards_data = json.loads(raw_cards)
        cards = [Card.model_validate(card) for card in cards_data]

        return cards


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    with open("mock_data/ppt-to-md.md") as f:
        example_content = f.read()

    card_creator = LLMCardCreator()
    cards = card_creator.create_cards(text=example_content, n_cards=None)
