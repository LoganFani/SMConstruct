import json
from llama_cpp import Llama, LlamaGrammar


class Translator:
    def __init__(self, model_path: str, grammar_path: str = "") -> None:
        self.llm = Llama(model_path=model_path, n_gpu_layers=0)
        self.grammar_path = grammar_path
        self._grammar: LlamaGrammar | None = self._load_grammar() if grammar_path else None

    def _load_grammar(self) -> LlamaGrammar:
        with open(self.grammar_path, "r") as f:
            return LlamaGrammar.from_string(f.read())

    def build_promptv2(self, input_content: str, sentence_context: str, from_lang: str, to_lang: str) -> str:
        return f"""
        You are a specialized language tutor.

        Return ONLY valid JSON matching this schema:
        {{
        "original_content": string,
        "translation": string,
        }}

        Rules:
        - Translate the input content based on the sentence context.
        - DO NOT translate the original_content field.
        - Do NOT include extra keys
        - Do NOT include explanations
        - Do NOT include markdown
        - Do NOT repeat fields
        - Match the tone/register of the sentence context (casual vs formal vs slang).
        - Never omit any field

        Original Language: {from_lang}
        Target Language: {to_lang}
        Original Content: {input_content}
        Sentence Context: {sentence_context}
        """

    def generate_response(self, prompt: str) -> dict:
        try:
            kwargs = dict(prompt=prompt, max_tokens=200, temperature=0.05, repeat_penalty=1.15)
            if self._grammar:
                kwargs["grammar"] = self._grammar
            output = self.llm(**kwargs)
            return json.loads(output["choices"][0]["text"])
        except Exception:
            return {}


# Module-level singleton — populated by lifespan on startup
translator: Translator | None = None


def init_translator(model_path: str, grammar_path: str = "") -> None:
    global translator
    translator = Translator(model_path, grammar_path)


def get_translator() -> Translator:
    if translator is None:
        raise RuntimeError("Translator has not been initialized. Call init_translator() first.")
    return translator