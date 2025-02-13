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
                    "name": "Card 1",
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

        return output_dir


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    deck_creator = AnkiDeckInterface()
    with open("../mock_data/ppt-to-md.md") as f:
        example_content = f.read()

    card_creator = LLMCardCreator()
    cards = card_creator.create_cards(text=example_content, n_cards=20)

    all_cards = {"../mock_data/ppt-to-md.md": cards}

    deck_creator.generate_deck(all_cards, deck_name="test2", output_dir="../mock_data/")
