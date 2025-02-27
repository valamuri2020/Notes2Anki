import os
import genanki
import random
from typing import List, Dict
from services.card_creator import Card
from services.logger import LoggerMixin
from services.exceptions import AnkiDeckGenerationError


class AnkiDeckInterface(LoggerMixin):
    def __init__(self):
        super().__init__()
        self.model = self._create_model()

    def _create_model(self):
        """Create the Anki card model."""
        self.logger.debug("Creating Anki model")
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
        self.logger.info(
            "Starting Anki deck generation",
            extra={
                "extra_fields": {
                    "deck_name": deck_name,
                    "num_files": len(all_cards),
                    "output_dir": output_dir
                }
            }
        )

        # Process deck name
        deck_name = deck_name.split(".apkg")[0] if ".apkg" in deck_name else deck_name
        self.logger.debug(f"Processed deck name: {deck_name}")

        # Create deck
        deck = genanki.Deck(deck_id=random.randrange(1 << 30, 1 << 31), name=deck_name)

        # Add cards to deck
        total_cards_added = 0
        for citation, cards in all_cards.items():
            self.logger.debug(
                "Processing cards from source",
                extra={
                    "extra_fields": {
                        "source": citation,
                        "num_cards": len(cards)
                    }
                }
            )
            
            for card in cards:
                note = genanki.Note(
                    model=self.model,
                    fields=[card.concept, card.description, citation]
                )
                deck.add_note(note)
                total_cards_added += 1

        # Save the deck
        try:
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, deck_name + ".apkg")
            
            self.logger.debug(
                "Generating Anki package",
                extra={
                    "extra_fields": {
                        "output_path": output_path,
                        "total_cards": total_cards_added
                    }
                }
            )
            
            genanki.Package(deck).write_to_file(output_path)
            
            self.logger.info(
                "Anki deck generation completed successfully",
                extra={
                    "extra_fields": {
                        "deck_name": deck_name,
                        "total_cards": total_cards_added,
                        "output_path": output_path
                    }
                }
            )
            
            return output_path
            
        except Exception as e:
            details = {
                "deck_name": deck_name,
                "output_dir": output_dir,
                "total_cards": total_cards_added,
                "error": str(e)
            }
            self.logger.error(
                "Error generating Anki deck",
                extra={"extra_fields": details}
            )
            raise AnkiDeckGenerationError("Failed to generate Anki deck", details=details)


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

    all_cards = {filename: cards}

    deck_creator = AnkiDeckInterface()
    deck_creator.generate_deck(all_cards, deck_name=filename.split(".")[0])
