import os

from groq import Groq

from app.config.settings import settings


class GroqClient:

    def __init__(self):

        self.client = Groq(
            api_key=settings.GROQ_API_KEY
        )

        self.model = settings.LLM_MODEL

    def generate(self, prompt):

        response = self.client.chat.completions.create(

            model=self.model,

            messages=[

                {
                    "role": "system",
                    "content": "You are FinSolve's AI Assistant."
                },

                {
                    "role": "user",
                    "content": prompt
                }

            ],

            temperature=0.2,

            max_tokens=1024

        )

        return response.choices[0].message.content