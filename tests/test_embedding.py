from app.ai.embedding_factory import get_embeddings

embedding_model = get_embeddings()

text = "The employee handbook explains the reimbursement policy."

vector = embedding_model.embed_query(text)

print("Embedding Model Loaded")

print("Vector Length :", len(vector))

print()

print("First 10 Values:")

print(vector[:10])