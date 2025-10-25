import os
from google import genai

google_api_key = "AIzaSyAdCvnxTFuXUCBLK3KX6rtzlyto1qaBA_U"

artwork = "Starry Night"
prompt = f"""
You are an art analysis assistant.
Artwork: {artwork}
Given a description, title, or image of an artwork, identify and extract structured information about it.
Output your answer in clear labeled categories as shown below.
If information is uncertain or not present, respond with “Unknown.”
Respond using JSON file
Respond with ONLY valid JSON. No explanation or text outside the JSON.

Extract the following:
Title of Artwork – the full name of the piece.


Artist(s) – the name(s) of the creator(s).


Date / Time Period / Era – approximate year, century, or historical period.


Nation or Region (at the time of creation) – the country, empire, or cultural context when it was made.


Art Movement or School – e.g., Impressionism, Surrealism, Baroque, Abstract Expressionism.


Medium / Materials – e.g., oil on canvas, marble sculpture, digital installation.


Style Characteristics – describe visual qualities (e.g., realistic, stylized, abstract, geometric, expressive).


Abstractness vs. Concreteness – classify as abstract, semi-abstract, or representational.


Subject Matter / Genre – e.g., portrait, landscape, still life, historical scene, mythological theme, conceptual art.


Main Themes or Ideas – key emotional, symbolic, or social topics (e.g., identity, nature, industrialization, spirituality).


Color Palette / Mood (optional) – brief description of dominant tones or emotional atmosphere.


Techniques or Distinctive Features (optional) – e.g., brushstroke texture, use of light, collage, installation scale.
"""

prompt_2 = f"""
You are an art recommendation assistant.
Given structured information about an artwork, suggest related artworks, artists, or movements that share similar qualities.
Base your suggestions on overlaps in themes, style, time period, technique, and cultural context.
Output response as a list of artworks with one in each line, breaking lines until all are present. Give 6 to 10 suggestions.

Your Task:
Analyze the provided metadata.

For each recommendation, include:

Title, (Artist, Where the artwork is located)

Metadata:
"Title of Artwork": "The Starry Night",
  "Artist(s)": "Vincent van Gogh",
  "Date / Time Period / Era": "June 1889 / Post-Impressionism",
  "Nation or Region (at the time of creation)": "France",
  "Art Movement or School": "Post-Impressionism",
  "Medium / Materials": "Oil on canvas",
  "Style Characteristics": "Highly stylized, expressive, dynamic, energetic, subjective use of color and form",
  "Abstractness vs. Concreteness": "Representational (but highly stylized and expressive)",
  "Subject Matter / Genre": "Nightscape / Landscape / Celestial Scene",
  "Main Themes or Ideas": "Spirituality, the power and infinity of nature, emotional turmoil, death and eternity",
  "Color Palette / Mood (optional)": "Dominant deep indigo and cobalt blues contrasted with vibrant yellows and whites; tumultuous yet awe-inspiring mood",
  "Techniques or Distinctive Features (optional)": "Heavy use of impasto (thick paint application), distinctive swirling and directional brushstrokes (often visible in short, thick strokes)"
"""

# Load API key from environment variable
client = genai.Client(api_key=os.getenv(google_api_key))

# Send a prompt to the model
response = client.models.generate_content(
    model="gemini-flash-latest",
    contents=prompt_2

)

print(response.text)
