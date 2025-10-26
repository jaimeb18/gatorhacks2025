from pathlib import Path
import google.generativeai as genai
import re
import requests
from config import google_api_key, google_places_api_key, model_name

class Agent:
    # API Keys loaded from config
    google_api_key = google_api_key
    google_places_api_key = google_places_api_key

    # Gemini Model
    model_name = model_name

    def __init__(self, media_type, name: str = ""):
        current_file = Path(__file__)
        current_directory = current_file.parent
        prompts = current_directory / "Prompts"
        if media_type == "artwork":
            self.__artwork = name

            #Gathering files
            self.__extracting_themes_prompt = (prompts / "Artworks_Extracting_Themes_Prompt.txt").read_text(
                encoding="utf-8")
            self.__get_suggestions_prompt = (prompts/ "Artworks_Get_Suggestions_Prompt.txt").read_text(
                encoding="utf-8")
            self.__get_details_prompt = (prompts/"Artworks_Get_Details_Prompt.txt").read_text(
                encoding="utf-8")
        elif media_type == "food":
            self.__dish_name = name

            #Gathering files
            self.__extracting_themes_prompt = (prompts / "Food_Extracting_Themes_Prompt.txt").read_text(
                encoding="utf-8")
            self.__get_details_prompt = (prompts / "Food_Get_Details_Prompt.txt").read_text(encoding="utf-8")
            self.__get_suggestions_prompt = (prompts / "Food_Get_Suggestions_Prompt.txt").read_text(encoding="utf-8")
        elif media_type == "architecture":
            self.__artwork = name

            # Gathering files
            self.__extracting_themes_prompt = (prompts / "Architecture_Extracting_Themes_Prompt.txt").read_text(
                encoding="utf-8")
            self.__get_details_prompt = (prompts / "Architecture_Get_Details_Prompt.txt").read_text(encoding="utf-8")
            self.__get_suggestions_prompt = (prompts / "Architecture_Get_Suggestions_Prompt.txt").read_text(encoding="utf-8")

        # Configure the API key
        genai.configure(api_key=Agent.google_api_key)
        self.__model = genai.GenerativeModel(Agent.model_name)

    def add_artwork_to_prompt(self):
        lines = self.__extracting_themes_prompt.splitlines()
        lines[1] += f" {self.__artwork}"
        self.__extracting_themes_prompt = "\n".join(lines)
        lines = self.__get_details_prompt.splitlines()
        lines[0] += f" {self.__artwork}"
        self.__get_details_prompt = "\n".join(lines)
        lines = self.__get_suggestions_prompt.splitlines()
        lines[0] = lines[0].replace("{artwork}", self.__artwork)
        self.__get_suggestions_prompt = "\n".join(lines)

    def add_food_to_prompt(self, location):
        lines = self.__extracting_themes_prompt.splitlines()
        lines[1] += f" {self.__dish_name}"
        self.__extracting_themes_prompt = "\n".join(lines)
        lines = self.__get_details_prompt.splitlines()
        lines[0] += f" {self.__dish_name}"
        self.__get_details_prompt = "\n".join(lines)
        lines = self.__get_suggestions_prompt.splitlines()
        lines[1] = lines[1].replace("{food}", self.__dish_name)
        lines[0] += f" {location}"
        self.__get_suggestions_prompt = "\n".join(lines)

    def add_architecture_to_prompt(self):
        lines = self.__extracting_themes_prompt.splitlines()
        lines[1] += f" {self.__artwork}"
        self.__extracting_themes_prompt = "\n".join(lines)
        lines = self.__get_details_prompt.splitlines()
        lines[0] += f" {self.__artwork}"
        self.__get_details_prompt = "\n".join(lines)
        lines = self.__get_suggestions_prompt.splitlines()
        lines[0] += f" {self.__artwork}"
        self.__get_suggestions_prompt = "\n".join(lines)

    def get_themes(self):
        response = self.__model.generate_content(self.__extracting_themes_prompt)
        return response.text

    def get_details(self):
        response = self.__model.generate_content(self.__get_details_prompt)
        return response.text

    def artwork_suggestions(self, themes):
        lines = self.__get_suggestions_prompt.splitlines()
        lines[-1] += themes
        self.__get_suggestions_prompt = "\n".join(lines)
        response = self.__model.generate_content(self.__get_suggestions_prompt)
        gemini_list = eval(re.sub(r'```python\n?|```\n?', '', response.text.strip()))
        suggestion_list = []
        for innerList in gemini_list:
            if type(innerList) is list:
                suggestion_list.append(
                    {"Name": innerList[0], "Artist": innerList[1], "Year": innerList[2],
                     "Current Location": innerList[3], "Wikipedia": innerList[4]
                     })
        return suggestion_list

    def food_suggestions(self, location, themes):
        lines = self.__get_suggestions_prompt.splitlines()
        lines[-1] += themes
        self.__get_suggestions_prompt = "\n".join(lines)
        response = self.__model.generate_content(self.__get_suggestions_prompt)
        gemini_list = eval(re.sub(r'```python\n?|```\n?', '', response.text.strip()))
        suggestion_list = []
        for innerList in gemini_list:
            if type(innerList) is list:
                append_this = {"Restaurant Name": innerList[0], "Cuisine": innerList[1], "Average Costs": innerList[2],
                     "Yelp Stars": innerList[3]}

                # Get Google Maps info
                url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
                params = {
                    "input": f"{append_this["Restaurant Name"]} in {location}",
                    "inputtype": "textquery",
                    "fields": "place_id,name,formatted_address,rating",
                    "key": Agent.google_places_api_key
                }
                response = requests.get(url, params=params).json()
                
                if response.get("candidates") and len(response["candidates"]) > 0:
                    place_info = response["candidates"][0]
                    place_id = place_info["place_id"]
                    usable_link = f"https://www.google.com/maps/place/?q=place_id:{place_id}"
                    append_this["Address"] = usable_link
                    # Get actual Google rating if Yelp stars are Unknown
                    if innerList[3] == "Unknown" and "rating" in place_info:
                        append_this["Yelp Stars"] = f"{place_info['rating']} (Google)"
                    else:
                        append_this["Yelp Stars"] = innerList[3]
                suggestion_list.append(append_this)
        return suggestion_list

    def architecture_suggestions(self, themes):
        lines = self.__get_suggestions_prompt.splitlines()
        lines[-1] += themes
        self.__get_suggestions_prompt = "\n".join(lines)
        response = self.__model.generate_content(self.__get_suggestions_prompt)
        gemini_list = eval(re.sub(r'```python\n?|```\n?', '', response.text.strip()))
        suggestion_list = []
        for innerList in gemini_list:
            if type(innerList) is list:
                append_this = {"Name": innerList[0], "Location": innerList[1], "Type Of Architecture": innerList[2],
                 "Era": innerList[3],"Wikipedia": innerList[4]
                }
                # Get Google Maps info
                url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
                params = {
                    "input": f"{append_this["Name"]} in {append_this["Location"]}",
                    "inputtype": "textquery",
                    "fields": "place_id,name,formatted_address,rating",
                    "key": Agent.google_places_api_key
                }
                response = requests.get(url, params=params).json()

                if response.get("candidates") and len(response["candidates"]) > 0:
                    place_info = response["candidates"][0]
                    place_id = place_info["place_id"]
                    usable_link = f"https://www.google.com/maps/place/?q=place_id:{place_id}"
                    append_this["Address"] = usable_link
                suggestion_list.append(append_this)
        return suggestion_list

my_agent = Agent("artwork", "St. Denis by Eduoard Cortes")
my_agent.add_artwork_to_prompt()
params = my_agent.get_themes()
print(my_agent.artwork_suggestions(params))
