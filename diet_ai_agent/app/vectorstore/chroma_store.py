class SimpleVectorStore:
    def __init__(self):
        self.knowledge = [
            "Egg contains high protein and about 78 calories.",
            "Rice is a high carbohydrate food.",
            "Chicken breast contains about 165 calories per 100g.",
            "Dal contains fiber and plant protein.",
            "Eating protein in breakfast helps control hunger.",
            "Vegetables should be part of every meal.",
            "Oats are high in fiber and good for digestion.",
            "Almonds contain healthy fats and protein.",
            "Greek yogurt is high in protein and probiotics.",
            "Salmon is rich in omega-3 fatty acids.",
            "Quinoa is a complete protein with all essential amino acids.",
            "Sweet potatoes are high in vitamin A and fiber.",
            "Broccoli is low in calories but high in nutrients.",
            "Avocado contains healthy monounsaturated fats.",
            "Lentils are high in protein and iron.",
            "Chia seeds are rich in omega-3s and fiber.",
            "Tofu is a good plant-based protein source.",
            "Berries are high in antioxidants and low in calories.",
            "Spinach is rich in iron and vitamins.",
            "Brown rice is a whole grain with more fiber than white rice."
        ]

    def search(self, query, k=3):
        """Simple search that returns the most relevant documents"""
        query_lower = (query or "").lower()
        if not query_lower.strip():
            return []

        # Token overlap scoring (tiny "semantic-ish" search without embeddings).
        stop = {
            "the", "a", "an", "and", "or", "vs", "versus", "for", "to", "of", "in", "on",
            "about", "me", "is", "are", "with", "weight", "loss", "gain", "help", "tell",
        }
        q_tokens = [t for t in "".join(ch if ch.isalnum() else " " for ch in query_lower).split() if t and t not in stop]
        if not q_tokens:
            q_tokens = query_lower.split()

        scored = []
        for doc in self.knowledge:
            doc_lower = doc.lower()
            score = 0.0
            # Strong bonus if any key token is present
            for t in q_tokens:
                if t in doc_lower:
                    score += 1.0
            # Extra boost for exact phrase hits (rare but nice)
            if query_lower in doc_lower:
                score += 2.0
            if score > 0:
                scored.append((score, doc))

        scored.sort(key=lambda x: x[0], reverse=True)
        results = []
        for score, doc in scored[:k]:
            results.append({"metadata": {"content": doc}, "score": float(score)})
        return results

# Create a simple vector store instance
simple_vector_store = SimpleVectorStore()

def lookup_food_knowledge(query):
    """Look up food-related knowledge from the simple vector store"""
    results = simple_vector_store.search(query, k=3)

    if not results:
        return "I couldn't find any information about that food. Please try a different query."

    response = f"Information about '{query}':\n\n"
    for i, result in enumerate(results, 1):
        response += f"{i}. {result['metadata']['content']}\n"

    return response.strip()

# Create a global instance for FastAPI
chroma_store = SimpleVectorStore()
