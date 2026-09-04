import os

from dotenv import load_dotenv
from google import genai


load_dotenv()


class GeminiLLM:

    def __init__(
        self,
        model: str = "gemini-3.6-flash",
    ):
        api_key = os.getenv("GEMINI_API_KEY") 

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not found in .env"
            )

        self.model = model

        self.client = genai.Client(
            api_key=api_key
        )

        print(
            f"Gemini LLM initialized: {self.model}"
        )

    def generate(
        self,
        prompt: str,
    ):

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )

        return response.text