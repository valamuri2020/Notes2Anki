import genanki
import fitz  # PyMuPDF
import random

# Open the PDF file
doc = fitz.open("path to pdf file")

# Specify the page number (0-indexed)
page_number = 0  # For example, third page

# Load the page and render it to an image
page = doc.load_page(page_number)
pix = page.get_pixmap()
image_filename = "page_0.png"
pix.save(image_filename)

# Define your model (ensure it supports HTML rendering)
my_model = genanki.Model(
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
            "name": "Q/A",
            "qfmt": "<div style='font-size: 26px;'>{{Question}}</div>",
            "afmt": """{{Answer}}<br>{{Image}}<br><br>
                     <small>Source: {{Source}}</small>
                     <div style='text-align: right;'><a href='https://notes2anki.com'>notes2anki.com</a></div>""",
        }
    ],
)

# Create a note with the image embedded
my_note = genanki.Note(
    model=my_model,
    fields=[
        "Generic Question",
        "content content content",
        "some generic source",
        f"<img src='{image_filename}' />",  # This will show the image on the back
    ],
)

# Create the deck and add the note
my_deck = genanki.Deck(2059400110, "My PDF Page Deck")
my_deck.add_note(my_note)

# Include the image in the media_files list so it gets packaged with the deck
package = genanki.Package(my_deck)
package.media_files = [image_filename]
package.write_to_file("output_deck.apkg")
