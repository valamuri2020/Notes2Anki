import os
import genanki
import random
import csv
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

    def _generate_pdf(self, all_cards: Dict[str, List[Card]], output_path: str) -> str:
        """Generate a PDF file containing all flashcards."""
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            
            doc = SimpleDocTemplate(output_path, pagesize=letter)
            styles = getSampleStyleSheet()
            elements = []

            # Create custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=14,
                spaceAfter=20
            )
            cell_style = ParagraphStyle(
                'CustomCell',
                parent=styles['Normal'],
                fontSize=10,
                leading=14
            )

            for source, cards in all_cards.items():
                # Add source as title
                elements.append(Paragraph(f"Source: {source}", title_style))
                elements.append(Spacer(1, 12))

                # Create table data
                data = [["Question", "Answer"]]
                for card in cards:
                    data.append([
                        Paragraph(card.concept, cell_style),
                        Paragraph(card.description, cell_style)
                    ])

                # Create and style the table
                table = Table(data, colWidths=[doc.width/2.0]*2)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('ROWSPLITOVERPAGE', (0, 0), (-1, -1), True),
                ]))
                elements.append(table)
                elements.append(Spacer(1, 20))

            doc.build(elements)
            return output_path
            
        except Exception as e:
            details = {
                "output_path": output_path,
                "error": str(e)
            }
            self.logger.error(
                "Error generating PDF",
                extra={"extra_fields": details}
            )
            raise AnkiDeckGenerationError("Failed to generate PDF", details=details)

    def _generate_csv(self, all_cards: Dict[str, List[Card]], output_path: str) -> str:
        """Generate a CSV file containing all flashcards."""
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Question', 'Answer', 'Source'])
                
                for source, cards in all_cards.items():
                    for card in cards:
                        writer.writerow([card.concept, card.description, source])
                        
            return output_path
            
        except Exception as e:
            details = {
                "output_path": output_path,
                "error": str(e)
            }
            self.logger.error(
                "Error generating CSV",
                extra={"extra_fields": details}
            )
            raise AnkiDeckGenerationError("Failed to generate CSV", details=details)

    def _generate_apkg(self, all_cards: Dict[str, List[Card]], deck_name: str, output_path: str) -> str:
        """Generate an Anki package file."""
        try:
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
            genanki.Package(deck).write_to_file(output_path)
            return output_path
            
        except Exception as e:
            details = {
                "deck_name": deck_name,
                "output_path": output_path,
                "error": str(e)
            }
            self.logger.error(
                "Error generating Anki package",
                extra={"extra_fields": details}
            )
            raise AnkiDeckGenerationError("Failed to generate Anki package", details=details)

    def generate_deck(
        self, all_cards: Dict[str, List[Card]], deck_name: str, 
        output_format: str = 'apkg', output_dir: str = "./tmp"
    ) -> str:
        """Generate a deck in the specified format."""
        self.logger.info(
            "Starting deck generation",
            extra={
                "extra_fields": {
                    "deck_name": deck_name,
                    "format": output_format,
                    "num_files": len(all_cards),
                    "output_dir": output_dir
                }
            }
        )

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Generate output path based on format
        base_name = deck_name.split(".")[0]  # Remove any existing extension
        output_path = os.path.join(output_dir, f"{base_name}.{output_format}")

        try:
            if output_format == 'apkg':
                return self._generate_apkg(all_cards, base_name, output_path)
            elif output_format == 'pdf':
                return self._generate_pdf(all_cards, output_path)
            elif output_format == 'csv':
                return self._generate_csv(all_cards, output_path)
            else:
                raise ValueError(f"Unsupported output format: {output_format}")

        except ValueError as e:
            details = {
                "deck_name": deck_name,
                "format": output_format,
                "output_dir": output_dir,
                "error": str(e)
            }
            self.logger.error(
                "Error generating deck",
                extra={"extra_fields": details}
            )
            raise AnkiDeckGenerationError(str(e), details=details)
        except Exception as e:
            details = {
                "deck_name": deck_name,
                "format": output_format,
                "output_dir": output_dir,
                "error": str(e)
            }
            self.logger.error(
                "Error generating deck",
                extra={"extra_fields": details}
            )
            raise AnkiDeckGenerationError("Failed to generate deck", details=details)


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
