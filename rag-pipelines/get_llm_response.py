from dsrag.llm import OpenAIChatAPI, AnthropicChatAPI

RESPONSE_SYSTEM_MESSAGE = """
You are a response generation system. Please generate a response to the user input based on the provided context. Your response should be as concise as possible while still fully answering the user's question.

Your response must ONLY be based on the provided context in the CONTEXT section below. Do not use any external information or knowledge. If the provided context is not sufficient to generate a response, you should indicate that you need more information.

CONTEXT
{context}
""".strip()

def get_response(question: str, context: str, model: str = "claude-3-5-sonnet-20240620"):
    openai_models = ["gpt-4o-mini", "gpt-4o", "gpt-4o-2024-08-06"]
    anthropic_models = ["claude-3-haiku-20240307", "claude-3-5-sonnet-20240620"]

    if model in openai_models:
        client = OpenAIChatAPI(model=model, temperature=0.0)
    elif model in anthropic_models:
        client = AnthropicChatAPI(model="claude-3-5-sonnet-20240620", temperature=0.0)
    else:
        raise ValueError(f"Model {model} is not supported.")
    
    chat_messages = [{"role": "system", "content": RESPONSE_SYSTEM_MESSAGE.format(context=context)}, {"role": "user", "content": question}]
    return client.make_llm_call(chat_messages)