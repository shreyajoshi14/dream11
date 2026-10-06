"""One command: download Cricsheet -> parse -> train ProductUI_Model (<= 2024-06-30) -> save artifacts."""
from .data_download import download
from .model_ui import load_history
from .train import train_product_model

if __name__ == "__main__":
    download()
    hist = load_history(rebuild=True)
    b = train_product_model(hist)
    print(b["meta"])
    print(b["importance"].head(10))
