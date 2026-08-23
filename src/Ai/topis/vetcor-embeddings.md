Vector Embeddings — A Practical Tutorial
1. What is a Vector Embedding?

A vector embedding is a way of turning something — a word, sentence, paragraph, image, or even a user profile — into a list of numbers (a vector) that captures its meaning in a way a computer can work with.


"The cat sat on the mat"  →  [0.021, -0.183, 0.442, ..., 0.077]   (e.g. 1536 numbers)

The key property: things that mean similar things end up close together in this numeric space, and things that mean different things end up far apart.

"king" and "queen"        → close together
"king" and "banana"       → far apart
"How do I reset my password?" and "I forgot my login" → close together

Distance in this space is usually measured with:

Cosine similarity — angle between two vectors (most common for text)
Euclidean distance — straight-line distance
Dot product — used when vectors are normalized

This is the entire foundation of semantic search, RAG, recommendation systems, and clustering.