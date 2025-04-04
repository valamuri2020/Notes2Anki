import os
from typing import List, Dict, Optional
import cohere
from pydantic import BaseModel
import json
from services.logger import LoggerMixin
from services.exceptions import LLMAPIError, LLMResponseError
import asyncio
from google import genai


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
## Introduction
    You are an expert tutor preparing study materials. Given this material, create flashcards designed to help students learn the *key concepts*. 
    A flashcard is defined as a pair of concept -> description mapping with an ID. Try not to repeat "concept" keys. Keep the descriptions concise yet with sufficient detail. 
    Focus on the fundamental ideas, principles, and topics that students need to understand to master the subject.
    
## Task
Create a *complete* set of flashcards that covers *all* the material. Ensure *every* distinct concept, idea, principle, and topic mentioned in the content is represented by at least one flashcard. There are certain types of information to ignore, which will be described later in the instructions.

Prioritize granularity. It's better to have too many specific flashcards than a few overly general ones. Prioritize brevity in the description of each card.
  
Group tightly related material together into one card. If concepts are part of a numbered or ordered sequence, maintain the numbering and structure within the description. For example, if a concept involves a list of steps, causes, or effects, ensure they are clearly delineated with commas in between them. Preserve original sequencing where applicable.   

Also, do not miss any key concepts. It is better to include an extra flashcard if you are unsure. Make sure each flashcard is self-contained, it should make sense if I pick it up on its own. References to other parts of the content that don't make sense without context are not suitable for flashcard-style learning. 
    
There may be <diagram></diagram> tags within the provided content. This represents a text summary of any images, charts, diagrams etc. There may be important material here so pay close attention. If a flashcard comes from content in a <diagram></diagram> tag, add '(from an image)' to the end of the description.
    
All information in the flashcards MUST come from the provided content enclosed in <content></content> tags. This is absolutely imperative and please do no hallucinate!

### What not to include in flashcards
    
Also, when creating flashcards, exclude administrative details, logistical information, course outlines, introductory remarks, summaries, or meta-discussions about the content itself.

Here are examples of types of information that should NOT be included in flashcards. It is VERY important you ignore this type of information for making flashcards.

    - Course mechanics (website links, office hours, etc.)
    - Course outlines (lists of topics)
    - Administrative details (grading policies, late submission rules, etc.)
    - Introductory or concluding remarks
    - Meta-discussions about the content (e.g., "This topic is important because...")
    - Anything not directly part of the core subject matter.
    - Irrelevant quotes

### Citations

We want to make sure that all information in the flashcards comes only and only from the information provided in the <content></content> tags. As part of the content, there may be page numbers included in the format "[[Page N]]", where N is the page number. 

If you are able to determine the page number, include it as part of the "page_num" key. If not, use -1.

### Format

Return an array of objects in JSON format, with each object having with the keys "id", "concept", "description", "page_num". 

## Summary
The task is to create "flashcards" given the material enclosed in <content></content>. Prioritize granularity, comprehensiveness and being concise in the description as possible. Do not include administrative details, logistical information, course outlines, introductory remarks, test logistics, summaries, or meta-discussions about the content itself. The flashcards must only contain concepts from the core content itself.

    <content>
    {}
    </content>
    """


class Card(BaseModel):
    id: int
    concept: str
    description: str
    page_num: int


class LLMCardCreator(LoggerMixin):
    def __init__(self):
        super().__init__()
        self.cohere_client = cohere.AsyncClientV2(api_key=os.getenv("COHERE_API_KEY"))
        self.google_client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

    def _keyword_deduplicate_file_content(self, text: str) -> str:
        return text

    def _semantic_deduplicate_file_content(self, text: str) -> str:
        return text

    async def create_cards(
        self,
        text: str,
        n_cards: Optional[int] = None,
        model: str = "gemini-2.0-flash",
    ) -> List[Card]:
        self.logger.info(
            "Starting flashcard creation",
            extra={
                "extra_fields": {
                    "content_length": len(text),
                    "n_cards": n_cards,
                    "model": model,
                }
            },
        )

        text = self._keyword_deduplicate_file_content(text)
        text = self._semantic_deduplicate_file_content(text)

        self.logger.debug("Creating cards with Cohere LLM")
        prompt = (
            Prompts.CREATE_CARDS_AUTO.format(text)
            if not n_cards
            else Prompts.CREATE_CARDS_N.format(n_cards, text)
        )

        try:
            # response = await self.cohere_client.chat(
            #     model=model,
            #     messages=[{"role": "user", "content": prompt}],
            # )

            response = await self.google_client.aio.models.generate_content(
                model=model,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": list[Card],
                },
            )

        except Exception as e:
            details = {"model": model, "error": str(e)}
            self.logger.error(
                "Failed to get response from {model}", extra={"extra_fields": details}
            )
            raise LLMAPIError("Failed to generate cards", details=details)

        # raw_cards = response.message.content[0].text
        raw_cards = response.text
        self.logger.debug("Parsing card response")

        try:
            cards_data = json.loads(raw_cards)
            cards = [Card.model_validate(card) for card in cards_data]
        except Exception as e:
            details = {"error": str(e), "response_text": raw_cards}
            self.logger.error(
                "Failed to parse model response", extra={"extra_fields": details}
            )
            raise LLMResponseError("Failed to parse model response", details=details)

        self.logger.info(
            "Flashcard creation completed",
            extra={"extra_fields": {"num_cards_created": len(cards)}},
        )

        return cards


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    with open("mock_data/Psych 257_with_page_nums.md") as f:
        example_content = f.read()

    # example_content = """
    # Architecturally, the school has a Catholic character. Atop the Main Building's gold dome is a golden statue of the Virgin Mary. Immediately in front of the Main Building and facing it, is a copper statue of Christ with arms upraised with the legend "Venite Ad Me Omnes". Next to the Main Building is the Basilica of the Sacred Heart. Immediately behind the basilica is the Grotto, a Marian place of prayer and reflection. It is a replica of the grotto at Lourdes, France where the Virgin Mary reputedly appeared to Saint Bernadette Soubirous in 1858. At the end of the main drive (and in a direct line that connects through 3 statues and the Gold Dome), is a simple, modern stone statue of Mary.
    # """

    card_creator = LLMCardCreator()
    cards = asyncio.run(card_creator.create_cards(text=example_content, n_cards=None))
    for card in cards:
        print(dict(card))
