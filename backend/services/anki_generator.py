import os
import genanki
import random
import csv
from typing import List, Dict
from typing import BinaryIO, List

from pydantic import BaseModel
from services.card_creator import Card
from services.file_processor import FileProcessor
from services.logger import LoggerMixin
from services.exceptions import AnkiDeckGenerationError
from fastapi import UploadFile
import fitz
import tempfile
from config import Settings
from services.card_creator import Card, LLMCardCreator


# TODO: anki cards with images cards
# TODO: sponsor cards


# class SponsorCardGenerator:
#     def __init__(self, sponsor_list_filepath: str):
#         self.
class ProcessedFileResult(BaseModel):
    cards: List[Card]
    file: UploadFile

    class Config:
        arbitrary_types_allowed = True


class AnkiDeckInterface(LoggerMixin):
    def __init__(self):
        super().__init__()
        self.qa_model = self._create_qa_model()
        self.qa_with_img_model = self._create_qa_with_img_model()
        settings = Settings()
        self.processor = FileProcessor(settings)

    def _create_qa_model(self):
        self.logger.debug("Creating Anki model")
        card_model = genanki.Model(
            model_id=random.randrange(1 << 30, 1 << 31),  # Generate a random Model ID
            name="QA-model",
            fields=[{"name": "Question"}, {"name": "Answer"}, {"name": "Source"}],
            templates=[
                {
                    # required field
                    "name": "Q/A",
                    "<div style='font-size: 26px;'>{{Question}}</div>"
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
    def _create_qa_with_img_model(self):
        self.logger.debug("Creating Anki model")
        card_model = genanki.Model(
            model_id=random.randrange(1 << 30, 1 << 31),  # Generate a random Model ID
            name="QA-img-model",
            fields=[
                {"name": "Question"},
                {"name": "Answer"},
                {"name": "Source"},
                {"name": "Image"},
            ],
            templates=[
                {
                    # required field
                    "name": "Q/A with image",
                    "qfmt": "<div style='font-size: 26px;'>{{Question}}</div>",
                    "afmt": """{{Answer}}<br>{{Image}}<br><br>
                            <small>Source: {{Source}}</small>""",
                }
            ],
        )

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        return card_model

    def _create_deck(
        self, deck_name: str, processed_file_results: List[ProcessedFileResult]
    ):
        # Process deck name
        deck_name = deck_name.split(".apkg")[0] if ".apkg" in deck_name else deck_name
        self.logger.debug(f"Processed deck name: {deck_name}")

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
        images_to_cleanup = []

        # Add cards to deck
        total_cards_added = 0
        for res in processed_file_results:
            citation = res.file.filename
            cards = res.cards
            file = res.file

            self.logger.debug(
                "Processing cards from source",
                extra={"extra_fields": {"source": citation, "num_cards": len(cards)}},
            )

            for card in cards:
                citation_with_page = (
                    f"{citation} - Page {card.page_num}"
                    if card.page_num != -1
                    else citation
                )

                # to only print it the first time
                DEBUG = 0
                # FIXME: tbh this is not a great way of detecting whether to include an image or not, but it does the job for now
                if "(from an image)" in card.description:
                    # Create a temporary file handle for the PDF data
                    if DEBUG == 0:
                        self.logger.debug("Making card with an image in it")
                        DEBUG += 1

                    # Reset file pointer to the beginning before reading
                    file.file.seek(0)

                    with tempfile.NamedTemporaryFile(delete=True) as temp_pdf:
                        temp_pdf.write(
                            file.file.read()
                        )  # Write file content to temp file
                        temp_pdf.flush()  # Ensure all data is written
                        doc = fitz.open(temp_pdf.name)  # Open using file path

                    # Reset file pointer again for potential future reads
                    file.file.seek(0)

                    page = doc.load_page(card.page_num - 1)
                    pix = page.get_pixmap()
                    image_filename = f"{res.file.filename}_page_{card.page_num}.png"
                    # cleanup happens after writing deck to a file
                    images_to_cleanup.append(image_filename)
                    pix.save(image_filename)

                    card.concept = card.concept.replace("(from an image)", "")
                    card.description = card.description.replace("(from an image)", "")

                    note = genanki.Note(
                        model=self.qa_with_img_model,
                        fields=[
                            card.concept,
                            card.description,
                            citation_with_page,
                            # This will show the image on the back
                            f"<img src='{image_filename}' />",
                        ],
                    )
                    pass
                else:
                    note = genanki.Note(
                        model=self.qa_model,
                        fields=[card.concept, card.description, citation_with_page],
                    )

                deck.add_note(note)
                total_cards_added += 1

        return deck, total_cards_added, images_to_cleanup

    def _write_deck_to_file(
        self,
        deck: genanki.Deck,
        total_cards_added: int,
        images_to_cleanup: List[str],
        deck_name: str,
        output_dir: str,
    ) -> str:
        try:
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, deck_name + ".apkg")

            self.logger.debug(
                "Generating Anki package",
                extra={
                    "extra_fields": {
                        "output_path": output_path,
                        "total_cards": total_cards_added,
                    }
                },
            )

            genanki.Package(deck, media_files=images_to_cleanup).write_to_file(
                output_path
            )

            self.logger.info(
                "Anki deck generation completed successfully",
                extra={
                    "extra_fields": {
                        "deck_name": deck_name,
                        "total_cards": total_cards_added,
                        "output_path": output_path,
                    }
                },
            )

            return output_path

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
                "total_cards": total_cards_added,
                "error": str(e),
            }
            self.logger.error(
                "Error generating Anki deck", extra={"extra_fields": details}
            )
            raise AnkiDeckGenerationError(
                "Failed to generate Anki deck", details=details
            )

        finally:
            # Clean up any image files that were created
            for image_path in images_to_cleanup:
                try:
                    if os.path.exists(image_path):
                        os.remove(image_path)
                        self.logger.debug(f"Deleted temporary image file: {image_path}")
                except Exception as e:
                    self.logger.warning(
                        f"Failed to delete temporary image file {image_path}: {str(e)}"
                    )

    async def process_single_file(self, file: UploadFile):
        self.logger.debug(
            f"Processing file", extra={"extra_fields": {"filename": file.filename}}
        )
        file_contents = await self.processor.process_file(file)
        creator = LLMCardCreator()
        cards = await creator.create_cards(file_contents)
        self.logger.debug(
            f"File processed successfully",
            extra={
                "extra_fields": {"filename": file.filename, "cards_created": len(cards)}
            },
        )
        return ProcessedFileResult(cards=cards, file=file)

    def generate_deck(
        self,
        processed_file_results: List[ProcessedFileResult],
        deck_name: str,
        output_dir="./tmp",
    ) -> str:
        self.logger.info(
            "Starting Anki deck generation",
            extra={
                "extra_fields": {
                    "deck_name": deck_name,
                    "num_files": len(processed_file_results),
                    "output_dir": output_dir,
                }
            },
        )

        deck, total_cards_added, images_to_cleanup = self._create_deck(
            deck_name, processed_file_results
        )
        output_path = self._write_deck_to_file(
            deck, total_cards_added, images_to_cleanup, deck_name, output_dir
        )

        return output_path, total_cards_added


if __name__ == "__main__":
    import io
    import sys
    from services.card_creator import Card, LLMCardCreator
    from dotenv import load_dotenv
    from config import Settings
    from fastapi import UploadFile
    from pprint import pprint
    import asyncio

    load_dotenv()
    demo_filepath = sys.argv[1]
    filename = os.path.basename(demo_filepath)

    with open(demo_filepath, "rb") as f:
        file_content = f.read()

    # use same interface as server to process file
    upload_file = UploadFile(file=io.BytesIO(file_content), filename=filename)

    deck_creator = AnkiDeckInterface()

    res = asyncio.run(deck_creator.process_single_file(upload_file))

    deck_creator.generate_deck([res], deck_name=filename.split(".")[0])
