from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

client = genai.Client()

long_context_pdf_path = "./mock_data/Psych 257_Anxiety & Obsession_W2025.pdf"

# Upload the PDF using the File API
sample_file = client.files.upload(
    file=long_context_pdf_path,
)

prompt_return_md = "Extract all the text in this document and return it as markdown"

prompt_gen_cards = """
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
"""

response = client.models.generate_content(
    model="gemini-1.5-flash",
    contents=[
        sample_file,
        "Label each image/figure in this file and tell me the meaning",
    ],
)
print(response.text)
