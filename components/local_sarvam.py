from pprint import pprint
from datetime import datetime
from imagine import ChatMessage, ImagineClient

# init client
print("Setting up client...")
client = ImagineClient(
    api_key="f66499e9-2d54-4adf-85c1-5c9d67a13b1b",
    endpoint="http://10.190.147.82:5050/v2"
)
print("Client connected.")


def generate_help(prompt: str):
    response = client.chat(
        messages=[
            # ChatMessage(role="user", content="Bharat ke baare mein batao?"),
            ChatMessage(role="user",
                        content=f"""
This is a detail about an application, act as a helper agent for this app and answer the question regarding:

HunarGyan is a smart assistant application built for Indian artisans such as weavers, potters, and woodworkers. The goal is to help artisans use digital technology **offline**, in their **local language**, without needing technical knowledge or internet access.

The app works offline-first, and when internet is available, the content generated can be published online. The assistant supports voice and text input and provides AI assistance for social media content, design ideas, and documentation.

Core features of HunarGyan:

1. DASHBOARD:
- Displays key metrics: 
  - Total crafts completed
  - Number of marketing contents created
  - Number of design ideas generated
- Shows recently created projects
- Provides quick actions:
  - Craft new document
  - Create marketing content
  - Get design ideas
  - View saved works

2. ARTISAN PROFILE:
- Stores:
  - Name
  - Phone number
  - Email ID
  - A short description
- The description is automatically enhanced by AI, based on past works/projects of the artisan.

3. DOCUMENT CRAFTING:
- Allows artisans to document their craft processes using:
  - Voice input
  - Text input
- Supports:
  - Adding images
  - Breaking the craft into multiple editable steps
  - Offline document creation and editing

4. MARKETING CONTENT GENERATOR:
- Lets artisans generate marketing materials using AI and templates:
  - Product description
  - Social media posts (with relevant trending hashtags)
  - Email newsletters
  - Website banners
- Customizable by:
  - Language (supports Indian regional languages)
  - Tone (e.g., friendly, formal, promotional)
  - Content type
- Users can view previously created marketing content

5. DESIGN IDEA GENERATOR:
- Artisans can upload a hand-drawn sketch
- AI analyzes the sketch and performs:
  - Sketch completion
  - Identification of required materials
  - Step-by-step guidance for completing the craft
- Also provides:
  - A gallery of similar inspirational designs
  - Option to generate design ideas from a text prompt (visual description)

6. SAVED WORKS:
- Displays all previous documents and marketing content
- Allows:
  - Viewing
  - Editing
  - Sharing
  - Saving/exporting

7. LANGUAGE & INPUT SUPPORT:
- All content creation supports regional Indian languages
- Both **voice** and **text input** are supported
- The assistant works entirely **offline**, except when publishing content online

The assistant is built to be culturally sensitive, easy to use for artisans with limited literacy or technical knowledge, and always prioritizes offline-first interaction and local language accessibility.

According to the above details answer this question: {prompt}
"""),
        ],
        model="Sarvam-m"
    )
    return response.first_content


def generate_document(
        user_name: str,
        steps: str
):
    resp = client.chat(
        messages = [
            ChatMessage(role="user", content=f"""
These are the steps to create a document for an artisan's craft:
{steps}
Generate a document for the artisan named {user_name} based on the above steps. The document should include:
1. Title: "Crafting Document for {user_name}"
2. Introduction: A brief introduction about the artisan and their craft.
3. Steps: A detailed breakdown of the steps involved in the craft, formatted as a numbered list.
4. Materials: A list of materials required for the craft.
5. Conclusion: A summary of the craft and its significance.
The document should be well-structured, easy to read, and suitable for sharing with others. Use a professional tone and ensure that the content is informative and engaging.
make the document as detailed as possible, and include any relevant information that would help someone understand the craft process.
also include the date of creation at the top of the document.
"""),
        ],
        model="Sarvam-m"
    )
    return resp.first_content


def ask(prompt: str):
    response = client.chat(
        messages=[
            ChatMessage(role="user", content=prompt),
        ],
        model="Sarvam-m"
    )
    return response.first_content


