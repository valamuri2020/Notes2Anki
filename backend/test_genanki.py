import genanki
import random

# Sample data - replace with your actual array of dictionaries
qa_pairs = [
    {'question': 'What is the capital of France?', 'answer': 'Paris'},
    {'question': 'What is the highest mountain in the world?', 'answer': 'Mount Everest'},
    {'question': 'What is the chemical symbol for water?', 'answer': 'H2O'}
]

# Define the card model
card_model = genanki.Model(
    model_id=random.randrange(1 << 30, 1 << 31), # Generate a random Model ID
    name='Simple-QA-Model',
    fields=[
        {'name': 'Question'},
        {'name': 'Answer'},
    ],
    templates=[
        {
            # required field
            'name': 'Card 1',
            'qfmt': '{{Question}}',
            'afmt': '{{Answer}}'
        }
    ]
)

# Create a new deck

# Purpose of IDs in Anki

# In Anki, both decks and card models are identified by unique IDs. These IDs serve a few important purposes:

# Uniqueness: Anki needs a way to distinguish between different decks and card models. If you have multiple decks or models, each must have a unique identifier so Anki can manage them separately.
# Database Integrity: Anki uses a database internally to store your decks, cards, and models. These IDs are crucial for maintaining relationships and references within the database. For example, when a card is created, it needs to be associated with a specific deck and a specific card model using these IDs.


deck = genanki.Deck(
    deck_id=random.randrange(1 << 30, 1 << 31),
    name='My Question Answer Deck'  # Replace with your desired deck name
)

# Loop through the question-answer pairs and create cards
for qa in qa_pairs:
    note = genanki.Note(
        model=card_model,
        fields=[qa['question'], qa['answer']]
    )
    deck.add_note(note)

# Output the deck to a .apkg file
output_filename = 'my_qa_deck.apkg' # Replace with your desired output file name
genanki.Package(deck).write_to_file(output_filename)

print(f"Anki deck '{output_filename}' created successfully with {len(qa_pairs)} cards.")