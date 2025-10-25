import os
from google import genai
import re
import json

while True:
    artwork = input("Enter the name of an artwork: ")

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

    prompt3 = (f"""
            Return a description of {artwork} using the following format: The [ARTWORK] was created by [ARTIST(s)] in
           [COUNTRY], [YEAR]. It is currently located in [LOCATION]. Add an extra sentence discussing the style, themes, historical context, or subject matter,
           depending on what you believe to be most relevant. Also provide the wikipedia link for {artwork}. Do not use
           asterisks or anything special around the words.
           
           Now, provide 6 suggestions for other similar artworks, following this guideline: the first four should be 
           findable in the same city, and the last two should be located in the same country.
           
           If {artwork} is not a known painting or sculpture, return simply "ERROR" and nothing else.
           """)

    prompt4 = f"""
            Analyze the given artwork, {artwork}, and identify six similar artworks. The first four should be findable
            in the same city as {artwork}, and the last two should be findable in the same country. For each of the six
            artworks, create a list in the given form ["artwork", "artist", "year created", "current location", wikipedia link"],
            replacing each of the strings with the actual artwork, artist, year created, current location, and wikipedia link.
            Return ONLY the six lists in valid Python list format that can be parsed, like: [["artwork1", "artist1", 
            "year1", "location1", "link1"], ["artwork2", "artist2", "year2", "location2", "link2"], ...]
            If {artwork} is not a known painting or sculpture, return simply "ERROR" and nothing else.
            """

    # Load API key from environment variable
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    # Send a prompt to the model
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents= prompt4

)
    '''
    if response.text == "ERROR":
        print("I do not recognize that artwork. Please try again.")
        print("")
    else:
        print(response.text)
        break
    '''

    geminiList = eval(re.sub(r'```python\n?|```\n?', '', response.text.strip()))
    suggestionList = []
    for innerList in geminiList:
        if type(innerList) is list:
            suggestionList.append(
                {"Name": innerList[0], "Artist" : innerList[1], "Year" : innerList[2],
                 "Current Location" : innerList[3], "Wikipedia" : innerList[4]
            })

    print(suggestionList)
    break
