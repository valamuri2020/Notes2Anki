import os
import genanki
import random
from typing import List, Dict, Optional
from services.card_creator import Card, LLMCardCreator


class AnkiDeckInterface:
    def __init__(self):
        self.model = self._create_model()

    def _create_model(self):
        card_model = genanki.Model(
            model_id=random.randrange(1 << 30, 1 << 31),  # Generate a random Model ID
            name="QA-Model",
            fields=[{"name": "Question"}, {"name": "Answer"}, {"name": "Source"}],
            templates=[
                {
                    # required field
                    "name": "Q/A",
                    "qfmt": "{{Question}}",
                    "afmt": "{{Answer}}<br><br><small>Source: {{Source}}</small>",
                }
            ],
        )
        return card_model

    def generate_deck(
        self, all_cards: Dict[str, List[Card]], deck_name: str, output_dir="./tmp"
    ) -> str:

        deck = genanki.Deck(deck_id=random.randrange(1 << 30, 1 << 31), name=deck_name)

        for citation, cards in all_cards.items():
            for card in cards:
                note = genanki.Note(
                    model=self.model, fields=[card.concept, card.description, citation]
                )
                deck.add_note(note)

        # Save the deck
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, deck_name + ".apkg")
        genanki.Package(deck).write_to_file(output_path)

        return output_path


if __name__ == "__main__":
    import io
    import sys
    from services.card_creator import Card, LLMCardCreator
    from services.file_processor import FileProcessor
    from dotenv import load_dotenv
    from config import Settings
    from fastapi import UploadFile
    from pprint import pprint

    load_dotenv()
    demo_filepath = sys.argv[1]
    filename = os.path.basename(demo_filepath)

    with open(demo_filepath, "rb") as f:
        file_content = f.read()

    # use same interface as server to process file
    upload_file = UploadFile(file=io.BytesIO(file_content), filename=filename)

    print("Created UploadFile")

    settings = Settings()
    processor = FileProcessor(settings)
    text = processor.process_file(upload_file)

    card_creator = LLMCardCreator()
    cards = card_creator.create_cards(text=text, n_cards=None)

    # all_cards = {filename: cards}

    # deck_creator = AnkiDeckInterface()
    # deck_creator.generate_deck(all_cards, deck_name=filename.split(".")[0])
