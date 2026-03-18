import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..')))

from src.rag.rag import RAG

def main():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'rag.yaml')
    real_RAG = RAG(config_path= config_path)
    real_RAG.display_chunks(num_samples=25)


if __name__ == "__main__":
    main()