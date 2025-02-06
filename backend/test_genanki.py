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
            'name': 'Card 1',
            'qfmt': '{{Question}}',
            'afmt': '{{Answer}}'
        }
    ]
)

# Create a new deck
deck_id = 1678905432  # Replace with a unique number if needed, or use random.randrange(1 << 30, 1 << 31)
deck = genanki.Deck(
    deck_id,
    'My Question Answer Deck'  # Replace with your desired deck name
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