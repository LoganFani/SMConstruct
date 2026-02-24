from llama_cpp import Llama, LlamaGrammar

MODEL_PATH = "llama/models/mistral-7b-instruct-v0.2.Q4_0.gguf"

def build_prompt(input_content: str, from_lang: str, to_lang:str) -> str:
    return f"""
You are a specialized language tutor.

Return ONLY valid JSON matching this schema:
{{
  "original_content": string,
  "translation": string,
  "example_sentence": string
}}

Rules:
- example_sentence MUST be in {from_lang}
- Do NOT include extra keys
- Do NOT include explanations
- Do NOT include markdown
- Do NOT repeat fields

Original Language: {from_lang}
Target Language: {to_lang}
Original Content: {input_content}

Rules:
- Match the tone/register of the original content (casual vs formal vs slang).
- example_sentence MUST be written in {from_lang}
- If unsure, write a simple, natural {from_lang} sentence using the same structure
- Never omit any field
"""

def get_grammar(grammar_path:str) -> LlamaGrammar:
    with open(grammar_path, 'r') as gf:
        content = gf.read()

        return LlamaGrammar.from_string(content)

llm = Llama(model_path=MODEL_PATH, n_gpu_layers=0)

prompt = build_prompt("yo me preguntaba si quieren algo", "Spanish", "English")
json_grammar = get_grammar("llama/grammar/json.gbnf")

model_output = llm(prompt=prompt, max_tokens=200, grammar=json_grammar, temperature=0.05, repeat_penalty=1.15)

print(model_output["choices"][0]["text"])