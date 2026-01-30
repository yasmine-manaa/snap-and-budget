from sentence_transformers import SentenceTransformer
from transformers import pipeline

# Modèle CLIP pour transformer les images en vecteurs [cite: 67, 68]
# Il crée des vecteurs de 512 dimensions compatibles avec Qdrant
vision_model = SentenceTransformer('clip-ViT-B-32')

# Modèle de langage pour générer les recommandations
text_generator = pipeline("text-generation", model="facebook/opt-125m")

def get_image_embedding(image):
    """Convertit une image PIL en vecteur [cite: 67]"""
    return vision_model.encode(image).tolist()

def generate_recommendation_text(product_name, price):
    """Génère un petit texte d'accompagnement [cite: 54, 55]"""
    prompt = f"Product: {product_name} at {price}$. This is a great choice because"
    result = text_generator(prompt, max_new_tokens=30, do_sample=True)
    return result[0]['generated_text']