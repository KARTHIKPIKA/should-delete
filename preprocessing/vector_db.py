import os
import faiss
import numpy as np
import pickle
from collections import defaultdict

from tqdm import tqdm


class ImageEmbeddingIndex:
    def __init__(self, embedding_dim):
        self.embedding_dim = embedding_dim

        # Initialize FAISS index
        self.index = faiss.IndexFlatL2(embedding_dim)
        self.patient_id_to_indices = defaultdict(list)
        self.index_to_metadata = {}

    def add_images(self, df, get_embedding):
        """Compute embeddings and store them in FAISS."""
        all_embeddings = []
        all_indices = []
        counter = len(self.index_to_metadata)  # Ensure indices continue correctly

        for _, row in tqdm(df.iterrows()):
            patient_id = row["patient_id"]
            for image_path in row["image_paths"]:
                file_name = os.path.basename(image_path).split(".")[0]
                embedding = get_embedding(image_path)
                all_embeddings.append(embedding)
                all_indices.append(counter)

                # Store metadata
                self.patient_id_to_indices[patient_id].append(counter)
                self.index_to_metadata[counter] = {
                    "file_name": file_name,
                    "patient_id": patient_id,
                }
                counter += 1

        if all_embeddings:
            all_embeddings = np.array(all_embeddings, dtype=np.float32)
            self.index.add(all_embeddings)

    def save_index(self, faiss_index_path, metadata_path):
        """Save the FAISS index and metadata."""
        faiss.write_index(self.index, faiss_index_path)
        with open(metadata_path, "wb") as f:
            pickle.dump(
                {
                    "patient_id_to_indices": self.patient_id_to_indices,
                    "index_to_metadata": self.index_to_metadata,
                },
                f,
            )

    def load_index(self, faiss_index_path, metadata_path):
        """Load the FAISS index and metadata."""
        self.index = faiss.read_index(faiss_index_path)
        with open(metadata_path, "rb") as f:
            data = pickle.load(f)
            self.patient_id_to_indices = data["patient_id_to_indices"]
            self.index_to_metadata = data["index_to_metadata"]

    def search(self, query, get_embedding, patient_id=None, top_k=5):
        """Retrieve top_k similar images within a given cluster (if specified)."""
        query_embedding = np.array([get_embedding(query)], dtype=np.float32)

        if patient_id is not None and patient_id in self.patient_id_to_indices:
            indices = self.patient_id_to_indices[patient_id]
            if not indices:
                return []
            sub_index = faiss.IndexFlatL2(self.embedding_dim)
            sub_embeddings = np.array(
                [self.index.reconstruct(i) for i in indices], dtype=np.float32
            )
            sub_index.add(sub_embeddings)
            _, nearest_indices = sub_index.search(query_embedding, top_k)
            nearest_indices = [indices[i] for i in nearest_indices[0]]
        else:
            raise ValueError(f"Patient ID {patient_id} not found in the index.")

        return [
            self.index_to_metadata[i]
            for i in nearest_indices
            if i in self.index_to_metadata
        ]
