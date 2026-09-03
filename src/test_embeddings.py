from embedding_model import EmbeddingModel


model = EmbeddingModel()


sentences = [
    "High blood pressure can damage the kidneys.",

    "Hypertension may cause renal damage.",

    "Bananas contain potassium.",
]


vectors = model.embed_documents(sentences)


for i, vector in enumerate(vectors):

    print(
        f"Sentence {i}: "
        f"{len(vector)} dimensions"
    )


similarity_ab = sum(
    a * b
    for a, b in zip(vectors[0], vectors[1])
)

similarity_ac = sum(
    a * b
    for a, b in zip(vectors[0], vectors[2])
)


print("\nSimilarity A ↔ B:")
print(similarity_ab)


print("\nSimilarity A ↔ C:")
print(similarity_ac)