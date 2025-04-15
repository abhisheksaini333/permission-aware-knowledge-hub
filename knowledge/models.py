import threading
import numpy as np


def mean_pool(hidden, mask):
    weights = mask[..., None]
    pooled = (hidden * weights).sum(axis=1) / np.maximum(weights.sum(axis=1), 1)
    return pooled / np.maximum(np.linalg.norm(pooled, axis=1, keepdims=True), 1e-9)


class MiniLMEncoder:
    def __init__(self, path):
        import torch
        from transformers import AutoTokenizer, AutoModel

        torch.set_num_threads(2)
        self.tokenizer = AutoTokenizer.from_pretrained(path, local_files_only=True)
        self.model = AutoModel.from_pretrained(path, local_files_only=True).eval()
        self.lock = threading.Lock()

    def encode(self, texts):
        import torch

        result = []
        with self.lock, torch.no_grad():
            for i in range(0, len(texts), 16):
                batch = self.tokenizer(
                    texts[i : i + 16],
                    padding=True,
                    truncation=True,
                    max_length=256,
                    return_tensors="pt",
                )
                hidden = self.model(**batch).last_hidden_state.cpu().numpy()
                result.extend(
                    mean_pool(hidden, batch["attention_mask"].cpu().numpy()).tolist()
                )
        return result


def generation_limits(max_tokens):
    if type(max_tokens) is not int or not 1 <= max_tokens <= 128:
        raise ValueError("Generation token budget must be 1..128")
    return dict(max_new_tokens=max_tokens, do_sample=False, num_beams=1)


class FlanGenerator:
    def __init__(self, path, max_tokens=64):
        import torch
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

        torch.set_num_threads(2)
        self.tokenizer = AutoTokenizer.from_pretrained(path, local_files_only=True)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            path, local_files_only=True
        ).eval()
        self.options = generation_limits(max_tokens)
        self.capacity = threading.BoundedSemaphore(1)

    def generate(self, prompt):
        import torch

        if not self.capacity.acquire(timeout=2):
            raise RuntimeError("Answer model is busy")
        try:
            batch = self.tokenizer(prompt, return_tensors="pt", truncation=False)
            if batch["input_ids"].shape[1] > 512:
                raise ValueError("Evidence exceeds model input limit")
            with torch.no_grad():
                output = self.model.generate(**batch, **self.options)
            return self.tokenizer.decode(output[0], skip_special_tokens=True)
        finally:
            self.capacity.release()
