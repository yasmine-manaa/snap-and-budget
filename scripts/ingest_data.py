import pandas as pd
import os
import json
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
import logging
import time

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration Qdrant
client = QdrantClient(
    url="https://09caa185-ecc1-4c6a-b213-37a4e89caa58.us-east4-0.gcp.cloud.qdrant.io:6333",
    api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.roZ0YmbDQdquuMy1d3-6sD9ifNk0OLgrV9o7qb_TKXM"
)

collection_name = "fashion_products"
model = SentenceTransformer('clip-ViT-B-32')

def ingest(batch_size=50):
    """Ingestion des produits Flipkart dans Qdrant"""
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_path, '..', 'data', 'flipkart_fashion_products_dataset.json')
    
    if not os.path.exists(json_path):
        logger.error(f"❌ Fichier {json_path} introuvable!")
        return
    
    logger.info("📖 Lecture du fichier JSON...")
    try:
        df = pd.read_json(json_path)
    except Exception as e:
        logger.error(f"❌ Erreur lecture JSON: {e}")
        return
    
    logger.info(f"📊 Nombre total de produits: {len(df)}")
    
    # Ingérer 1000 produits
    df = df.head(1000)
    
    # Récréer la collection
    try:
        logger.info("🗑️ Suppression de la collection existante...")
        client.delete_collection(collection_name=collection_name)
    except:
        pass
    
    logger.info("✨ Création de la collection...")
    client.recreate_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(size=512, distance=models.Distance.COSINE)
    )
    
    # Batch processing
    points = []
    successful = 0
    failed = 0
    
    for i, row in df.iterrows():
        try:
            # Nettoyer le prix
            raw_price = str(row.get('selling_price', row.get('actual_price', '0')))
            price = float(raw_price.replace('₹', '').replace(',', '').strip())
            
            if price <= 0:
                price = float(str(row.get('actual_price', '0')).replace('₹', '').replace(',', '').strip() or '0')
            
            if price <= 0:
                failed += 1
                continue
            
            # Récupérer l'image URL
            images = row.get('image', [])
            if isinstance(images, str):
                try:
                    images = eval(images)
                except:
                    images = [images]
            
            img_url = images[0] if images else 'https://via.placeholder.com/100'
            
            # Créer un vecteur à partir du texte du produit
            product_text = f"{row.get('title', '')} {row.get('category', '')} {row.get('description', '')}"
            
            # Générer le vecteur via le modèle CLIP
            try:
                vector = model.encode(product_text[:500], convert_to_tensor=False).tolist()
            except:
                vector = model.encode(str(row.get('product_name', 'product'))[:200], convert_to_tensor=False).tolist()
            
            # Créer le point
            point = models.PointStruct(
                id=i,
                vector=vector,
                payload={
                    "name": str(row.get('title', 'Unknown'))[:100],
                    "price": price,
                    "category": str(row.get('category', ''))[:200],
                    "image_url": img_url,
                    "original_price": float(str(row.get('actual_price', '0')).replace('₹', '').replace(',', '').strip() or price)
                }
            )
            
            points.append(point)
            successful += 1
            
            if len(points) >= batch_size:
                logger.info(f"📤 Upload batch de {len(points)} produits...")
                try:
                    client.upsert(collection_name=collection_name, points=points)
                    points = []
                except Exception as e:
                    logger.warning(f"⚠️ Erreur batch: {e}")
                    time.sleep(1)
            
            if (successful + failed) % 100 == 0:
                logger.info(f"✅ {successful} réussis | ❌ {failed} échoués | Progress: {i}/{len(df)}")
                    
        except Exception as e:
            logger.debug(f"⚠️ Erreur item {i}: {e}")
            failed += 1
            continue
    
    # Upload final
    if points:
        logger.info(f"📤 Upload final de {len(points)} produits...")
        try:
            client.upsert(collection_name=collection_name, points=points)
        except Exception as e:
            logger.warning(f"⚠️ Erreur upload final: {e}")
    
    logger.info(f"""
    ✅ Ingestion terminée!
    - Produits réussis: {successful}
    - Produits échoués: {failed}
    - Total: {successful + failed}
    - URL Qdrant: https://cloud.qdrant.io
    """)

if __name__ == "__main__":
    ingest(batch_size=50)
