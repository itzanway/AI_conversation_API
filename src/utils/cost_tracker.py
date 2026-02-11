MODEL_PRICES_PER_1K = {
    "llama-3.1-8b-instant": {"input": 0.00005, "output": 0.00008},
    "gemma2-9b-it": {"input": 0.0001, "output": 0.0001},
}


def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    price = MODEL_PRICES_PER_1K.get(model, {"input": 0.0001, "output": 0.0001})
    return round((input_tokens / 1000 * price["input"]) + (output_tokens / 1000 * price["output"]), 8)
