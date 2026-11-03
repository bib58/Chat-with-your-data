"""
The 5 models under test, as OpenRouter slugs.
"""
MODELS = [
    ("Grok 4.5",         "x-ai/grok-4.5"),
    ("Kimi K3",          "moonshotai/kimi-k3"),
    ("Claude Sonnet 5",  "anthropic/claude-sonnet-5"),
    ("Gemini 3.8 Flash", "google/gemini-3.8-flash"),
    ("GPT-5.6 Terra",    "openai/gpt-5.6-terra-pro")
]

if __name__ == "__main__":
    print(f"{len(MODELS)} models under test:")
    for name, slug in MODELS:
        print(f"  {name:18s} -> {slug}")