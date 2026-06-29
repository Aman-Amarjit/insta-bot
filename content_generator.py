import re
import json
import config
from groq import Groq

class ContentGenerator:
    def __init__(self):
        self.api_key = config.GROQ_API_KEY
        if not self.api_key:
            print("⚠️ ContentGenerator warning: GROQ_API_KEY is missing.")
            print("Running in Mock content generator mode.")
            self.client = None
        else:
            try:
                self.client = Groq(api_key=self.api_key)
            except Exception as e:
                print(f"❌ Failed to initialize Groq client: {e}")
                self.client = None

    def _clean_json_text(self, raw_text: str) -> str:
        """
        Extracts the JSON substring between the first '{' and last '}' to strip
        conversational text or markdown code blocks (e.g. ```json ... ```).
        """
        raw_text = raw_text.strip()
        match = re.search(r'(\{.*\})', raw_text, re.DOTALL)
        if match:
            return match.group(1)
        return raw_text

    def _get_mock_fact(self, category: str) -> dict:
        """
        Returns a high-quality mock fact for local dry-runs when API key is missing.
        """
        return {
            "fact": f"Honey never expires; archaeologists found 3000-year-old honey edible in Egypt.",
            "explanation": "Its low moisture content and high acidity prevent the growth of bacteria and other microorganisms. This means it can sit on a shelf indefinitely without spoiling.",
            "category": category,
            "image_prompt": "minimalist dark background infographic showing honey jar and pyramid",
            "caption": "🍯 Honey is literally immortal.\n\nArchaeologists discovered 3000-year-old honey in Egyptian tombs — still perfectly edible. Its low moisture and acidic pH create a hostile environment for bacteria.\n\nWhat other foods do you think last forever? Drop your answer below 👇\n\n#facts #didyouknow #sciencefacts",
            "hashtags": ["facts", "didyouknow", "sciencefacts", "historyfacts", "amazingfacts", "todayilearned"]
        }

    def generate(self, category: str, recent_facts: list, is_retry: bool = False) -> dict:
        """
        Queries Groq to generate a fact in the specified category, excluding any recent facts.
        Includes full regex cleaning, JSON mode, and single-retry fallback logic.
        """
        if not self.client:
            print("Mock Generator: Returning pre-configured mock fact.")
            return self._get_mock_fact(category)

        recent_facts_str = json.dumps(recent_facts)
        
        system_instructions = (
            "You are a facts content creator for Instagram. "
            "You must output valid JSON only. Do not include markdown code fences (```json) in your final output, "
            "just raw JSON. Ensure all keys and string values are wrapped in double quotes."
        )

        user_prompt = f"""Generate ONE surprising, verified, little-known fact from this category: {category}

Return JSON with this schema:
{{
  "fact": "The actual fact in one clear, concise sentence suitable for an infographic",
  "explanation": "2-3 sentences expanding on the fact",
  "category": "{category}",
  "image_prompt": "minimalist dark background infographic showing: [visual description of the fact]",
  "caption": "Hook line\\n\\nFact explanation\\n\\nCall to action",
  "hashtags": ["facts", "didyouknow", "science", ...20 total]
}}

Rules:
- Fact must be verifiable and accurate.
- Must be surprising and not commonly known.
- One fact per post only.
- Never repeat a fact already in this list: {recent_facts_str}
"""

        # For retries, we enforce a stricter instruction set
        if is_retry:
            system_instructions += " CRITICAL: Your previous response failed to parse as JSON. You must strictly output valid JSON matching the requested schema. Do not output any preamble or postamble."

        try:
            # Query Groq with JSON Mode enabled
            completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_instructions},
                    {"role": "user", "content": user_prompt}
                ],
                model="llama-3.1-8b-instant",
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=800
            )

            raw_response = completion.choices[0].message.content
            cleaned_response = self._clean_json_text(raw_response)
            
            try:
                fact_data = json.loads(cleaned_response)
                
                # Basic validation of keys
                required_keys = ["fact", "explanation", "category", "caption", "hashtags"]
                for key in required_keys:
                    if key not in fact_data:
                        raise ValueError(f"Missing key '{key}' in JSON response")
                
                return fact_data
                
            except (json.JSONDecodeError, ValueError) as json_err:
                print(f"⚠️ JSON parsing failed on attempt (is_retry={is_retry}): {json_err}")
                print(f"Raw response was: {raw_response[:200]}...")
                
                if not is_retry:
                    print("🔄 Retrying fact generation with stricter prompt...")
                    return self.generate(category, recent_facts, is_retry=True)
                else:
                    raise json_err

        except Exception as e:
            print(f"❌ Failed to generate fact via Groq API: {e}")
            # In a production runner, we fail loud here, but let's fall back to mock if testing locally
            if not self.api_key:
                return self._get_mock_fact(category)
            raise e
