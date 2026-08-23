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



2. Why Not Just Use Keywords?

Keyword search (like SQL LIKE or Postgres full-text search) matches exact words. It fails on:

Query	Document	Keyword match?	Should match?
"car"	"automobile"	❌ No	✅ Yes
"cheap flights"	"affordable airfare"	❌ No	✅ Yes
"apple" (fruit)	"Apple" (company)	✅ Yes	❌ No

Embeddings solve the first two problems by capturing meaning, not exact spelling — but note the third row: embeddings alone don't solve ambiguity, they just shift where the problem lives (context in the surrounding text helps disambiguate).

3. How Embeddings Are Actually Created

At a high level, every embedding model does the same job: it's a neural network trained so that semantically similar inputs produce numerically similar output vectors.

3.1 Classic approaches (good to know, mostly legacy now)

One-Hot Encoding Each word gets a vector with a single 1 and the rest 0s. No notion of similarity at all — "cat" and "dog" are just as different as "cat" and "car". Rarely used directly anymore, but it's the conceptual starting point.

TF-IDF (Term Frequency–Inverse Document Frequency) Weighs words by how often they appear in a document vs. how rare they are across all documents. Still purely statistical — "car" and "automobile" are unrelated to it. Used today mostly for keyword/BM25 hybrid search, not semantic meaning.

Word2Vec / GloVe (2013–2014) The first real breakthrough. Trained on the idea that "a word is defined by the company it keeps." Words that appear in similar contexts get similar vectors.