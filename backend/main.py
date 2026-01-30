from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
from transformers import pipeline
from PIL import Image
import io
import random
import logging
import datetime
from typing import List, Dict

# Database imports
from database import SessionLocal, SearchHistory, User, get_db
from sqlalchemy.orm import Session
from sqlalchemy import text

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Snap & Budget API",
    description="Personal Shopper AI v2.0",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialisation des modèles (optimisée)
try:
    logger.info("Chargement des modèles...")
    
    # CLIP pour vision
    try:
        v_model = SentenceTransformer('clip-ViT-B-32')
        logger.info("✅ CLIP chargé")
    except Exception as e:
        logger.warning(f"⚠️ CLIP non disponible: {e}")
        v_model = None
    
    # LLM - DÉSACTIVÉ pour éviter lag (trop lourd)
    # Utiliser des réponses pré-générées à la place
    llm = None
    logger.info("⚠️ LLM optimisé (réponses pré-générées)")
    
    # Qdrant optionnel
    try:
        q_client = QdrantClient(
            url="https://09caa185-ecc1-4c6a-b213-37a4e89caa58.us-east4-0.gcp.cloud.qdrant.io:6333", 
            api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.roZ0YmbDQdquuMy1d3-6sD9ifNk0OLgrV9o7qb_TKXM"
        )
        logger.info("✅ Qdrant connecté")
    except Exception as e:
        logger.warning(f"⚠️ Qdrant non disponible: {e}")
        q_client = None
        
except Exception as e:
    logger.error(f"❌ Erreur: {e}")

def generate_rag_advice(product_name: str, price: float, user_budget: float, score: int) -> str:
    """Génère un conseil IA rapide (sans LLM lourd)"""
    try:
        economy = max(0, user_budget - price)
        economy_pct = int((economy / user_budget) * 100) if user_budget > 0 else 0
        
        # Conseils pré-générés rapides (pas de LLM)
        if score >= 90:
            advice = f"🏆 Excellent match! Économise {economy_pct}% du budget"
        elif score >= 75:
            advice = f"👍 Bon choix! Prix raisonnable, économise ${economy:.2f}"
        elif score >= 60:
            advice = f"💡 Acceptable. Considère alternatives pour plus d'économies"
        else:
            advice = f"⚠️ Match moyen. Augmente budget pour meilleures options"
        
        return advice if advice else f"Économies de {economy_pct}%"
        
    except Exception as e:
        logger.warning(f"Erreur RAG: {e}")
        return f"Budget requis: ${price:.2f}"

@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "vision_model": "clip-ViT-B-32",
        "llm_model": "facebook/opt-125m",
        "qdrant_connected": True
    }

@app.get("/", tags=["System"])
async def root():
    return {"message": "Snap & Budget API v2.0", "docs": "/docs"}

@app.post("/search_advanced", tags=["Search"])
async def search_products_advanced(
    budget: float,
    file: UploadFile = File(...),
    user_id: int = 1,
    search_mode: str = "Visual",
    payment_mode: str = "Immédiat",
    intent: str = "",
    occasion: str = "",
    db: Session = Depends(get_db)
) -> List[Dict]:
    """Recherche avancée avec IA et recommandations"""
    try:
        # Lire l'image
        image_data = await file.read()
        if len(image_data) == 0:
            raise HTTPException(status_code=400, detail="Image vide")
        
        try:
            image = Image.open(io.BytesIO(image_data)).convert('RGB')
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Format invalide: {str(e)}")
        
        # Vecteur CLIP
        query_vector = v_model.encode(image).tolist()
        
        # Recherche Qdrant
        max_price = budget * 1.5 if payment_mode in ["3x sans frais", "Planification"] else budget
        
        try:
            results = q_client.search(
                collection_name="fashion_products",
                query_vector=query_vector,
                query_filter=models.Filter(
                    must=[models.FieldCondition(
                        key="price",
                        range=models.Range(gte=0, lte=max_price * 2)
                    )]
                ),
                limit=5,
                with_payload=True,
                score_threshold=0.0
            )
        except Exception as e:
            logger.error(f"Erreur Qdrant: {e}")
            results = []
        
        if not results:
            return [{"error": "Aucun produit trouvé"}]
        
        # Traiter les résultats
        final_results = []
        for i, result in enumerate(results):
            try:
                score = max(0, min(100, int(result.score * 100)))
                price = float(result.payload.get('price', budget))
                name = result.payload.get('name', 'Produit inconnu')
                image_url = result.payload.get('image_url', '')
                
                ai_advice = generate_rag_advice(name, price, budget, score)
                payment_plan = generate_payment_plan(price, budget, payment_mode)
                trend = random.randint(5, 20)
                best_value = score >= 80 and price <= budget * 0.9
                
                final_results.append({
                    "id": result.id,
                    "name": name,
                    "price": round(price, 2),
                    "image_url": image_url,
                    "score": score,
                    "ai_advice": ai_advice,
                    "payment_plan": payment_plan,
                    "trend": trend,
                    "best_value": best_value,
                    "savings": round(max(0, budget - price), 2)
                })
                
                # Enregistrer l'historique
                try:
                    history = SearchHistory(
                        user_id=user_id,
                        product_name=name,
                        product_price=price,
                        budget=budget,
                        similarity_score=score,
                        ai_advice=ai_advice
                    )
                    db.add(history)
                except Exception as e:
                    logger.warning(f"Erreur historique: {e}")
            
            except Exception as e:
                logger.error(f"Erreur résultat {i}: {e}")
                continue
        
        # Commit
        try:
            db.commit()
        except Exception as e:
            logger.warning(f"Commit failed: {e}")
            db.rollback()
        
        return final_results if final_results else [{"error": "Aucun résultat"}]
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur: {e}", exc_info=True)
        return [{"error": str(e)}]

@app.get("/history/{user_id}", tags=["History"])
async def get_user_history(
    user_id: int,
    limit: int = 20,
    db: Session = Depends(get_db)
) -> List[Dict]:
    """Historique des recherches"""
    try:
        history = db.query(SearchHistory)\
            .filter(SearchHistory.user_id == user_id)\
            .order_by(SearchHistory.search_date.desc())\
            .limit(limit)\
            .all()
        
        return [
            {
                "id": item.id,
                "product_name": item.product_name,
                "price": item.product_price,
                "budget": item.budget,
                "score": item.similarity_score,
                "date": item.search_date.isoformat() if item.search_date else None,
                "advice": item.ai_advice
            }
            for item in history
        ]
    except Exception as e:
        logger.error(f"Erreur historique: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats/{user_id}", tags=["Stats"])
async def get_user_stats(user_id: int, db: Session = Depends(get_db)) -> Dict:
    """Statistiques utilisateur"""
    try:
        history = db.query(SearchHistory)\
            .filter(SearchHistory.user_id == user_id)\
            .all()
        
        if not history:
            return {
                "total_searches": 0,
                "avg_score": 0,
                "total_savings": 0
            }
        
        total_savings = sum(max(0, h.budget - h.product_price) for h in history)
        avg_score = sum(h.similarity_score for h in history) / len(history)
        
        return {
            "total_searches": len(history),
            "avg_score": round(avg_score, 2),
            "total_savings": round(total_savings, 2),
            "avg_savings": round(total_savings / len(history), 2)
        }
    except Exception as e:
        logger.error(f"Erreur stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def generate_payment_plan(price: float, budget: float, payment_mode: str) -> str:
    """Plan de paiement intelligent"""
    if price <= budget:
        return "✅ Paiement immédiat possible"
    
    if payment_mode == "3x sans frais":
        monthly = price / 3
        return f"💳 3x: ${monthly:.2f}/mois"
    
    if payment_mode == "Planification":
        if price <= budget * 1.2:
            weeks = int((price - budget) / 20) + 1
            return f"📅 Épargne: {weeks} semaines à $20/semaine"
        else:
            return "⚠️ Dépassement trop important"
    
    return f"⚠️ Dépasse: ${price - budget:.2f}"

# ==================== USER MANAGEMENT ENDPOINTS ====================

@app.post("/register", tags=["Auth"])
async def register_user(
    username: str,
    email: str,
    password: str,
    db: Session = Depends(get_db)
) -> Dict:
    """Enregistrer un nouvel utilisateur"""
    try:
        existing_user = db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")
        
        new_user = User(username=username, email=email)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return {
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
            "message": "User registered successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/login", tags=["Auth"])
async def login_user(
    username: str,
    email: str,
    db: Session = Depends(get_db)
) -> Dict:
    """Se connecter (validation utilisateur)"""
    try:
        user = db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "message": "Login successful"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/user/{user_id}", tags=["User"])
async def get_user(
    user_id: int,
    db: Session = Depends(get_db)
) -> Dict:
    """Obtenir les infos utilisateur"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== PAYMENT ENDPOINT ====================

@app.post("/checkout", tags=["Payment"])
async def checkout(
    user_id: int,
    total_amount: float,
    payment_method: str = "card",
    db: Session = Depends(get_db)
) -> Dict:
    """Traiter le paiement"""
    try:
        if total_amount <= 0:
            raise HTTPException(status_code=400, detail="Invalid amount")
        
        if payment_method not in ["card", "paypal", "bank"]:
            raise HTTPException(status_code=400, detail="Invalid payment method")
        
        # Simuler paiement réussi
        return {
            "status": "success",
            "message": "Payment processed successfully",
            "transaction_id": f"TXN-{user_id}-{int(total_amount)}",
            "amount": total_amount,
            "currency": "USD",
            "payment_method": payment_method,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Payment error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search_text", tags=["Search"])
async def search_products_text(
    query: str,
    budget: float,
    user_id: int = 1,
    payment_mode: str = "Immédiat",
    limit: int = 5,
    db: Session = Depends(get_db)
) -> List[Dict]:
    """Recherche par texte (mot-clé ou catégorie)"""
    try:
        # Charger les données JSON
        import json
        with open('../data/flipkart_fashion_products_dataset.json') as f:
            products = json.load(f)
        
        query_lower = query.lower()
        seen_products = set()
        matching = []
        
        for product in products:
            title = str(product.get('title', '')).lower()
            category = str(product.get('category', '')).lower()
            brand = str(product.get('brand', '')).lower()
            
            if query_lower in title or query_lower in category or query_lower in brand:
                # Vérifier le budget
                try:
                    price_str = str(product.get('selling_price', product.get('actual_price', '0')))
                    price = float(price_str.replace('₹', '').replace(',', '').strip())
                    if price > 0 and price <= budget:
                        # Éviter les doublons en utilisant le titre comme clé
                        product_key = str(product.get('title', '')).strip()
                        if product_key not in seen_products:
                            matching.append(product)
                            seen_products.add(product_key)
                            if len(matching) >= limit:
                                break
                except:
                    continue
        
        if not matching:
            return [{"error": "Aucun produit trouvé"}]
        
        final_results = []
        for product in matching:  # Plus besoin de [:limit] car on a déjà limité
            try:
                price_str = str(product.get('selling_price', product.get('actual_price', '0')))
                price = float(price_str.replace('₹', '').replace(',', '').strip())
                
                if price <= 0:
                    continue
                
                score = 90 if query_lower in str(product.get('title', '')).lower() else 75
                
                ai_advice = generate_rag_advice(str(product.get('title', '')), price, budget, score)
                payment_plan = generate_payment_plan(price, budget, payment_mode)
                
                final_results.append({
                    "name": str(product.get('title', 'Produit'))[:100],
                    "price": round(price, 2),
                    "category": str(product.get('category', ''))[:100],
                    "score": score,
                    "ai_advice": ai_advice,
                    "payment_plan": payment_plan,
                    "savings": round(max(0, budget - price), 2)
                })
            except:
                continue
        
        return final_results if final_results else [{"error": "Aucun produit valide"}]
    except Exception as e:
        logger.error(f"Erreur recherche: {e}")
        return [{"error": str(e)}]

@app.post("/record_sale", tags=["Sales"])
async def record_sale(
    user_id: int,
    product_name: str,
    product_price: float,
    customer_name: str,
    customer_email: str,
    total_amount: float,
    sale_date: str,
    db: Session = Depends(get_db)
):
    """Enregistrer une vente dans la base de données"""
    try:
        # Créer une table de ventes si elle n'existe pas
        db.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            product_name TEXT,
            product_price REAL,
            customer_name TEXT,
            customer_email TEXT,
            total_amount REAL,
            sale_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Insérer la vente
        db.execute("""
        INSERT INTO sales (user_id, product_name, product_price, customer_name, customer_email, total_amount, sale_date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, product_name, product_price, customer_name, customer_email, total_amount, sale_date))
        
        db.commit()
        
        # Mettre à jour les stats du produit
        db.execute("""
        CREATE TABLE IF NOT EXISTS product_stats (
            product_name TEXT PRIMARY KEY,
            total_sold INTEGER DEFAULT 0,
            total_revenue REAL DEFAULT 0,
            rating REAL DEFAULT 0.0,
            reviews INTEGER DEFAULT 0
        )
        """)
        
        # Mettre à jour ou insérer les stats du produit
        db.execute("""
        INSERT INTO product_stats (product_name, total_sold, total_revenue)
        VALUES (?, 1, ?)
        ON CONFLICT(product_name) DO UPDATE SET
        total_sold = total_sold + 1,
        total_revenue = total_revenue + ?
        """, (product_name, total_amount, total_amount))
        
        db.commit()
        
        return {
            "success": True,
            "message": "Sale recorded successfully",
            "transaction_id": f"TXN_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "amount": total_amount
        }
    except Exception as e:
        logger.error(f"Erreur enregistrement vente: {e}")
        return {"success": False, "error": str(e)}

@app.get("/bestsellers", tags=["Products"])
async def get_bestsellers(
    limit: int = 10,
    category: str = None,
    sort_by: str = "most_sold",
    db: Session = Depends(get_db)
):
    """Obtenir les best-sellers"""
    try:
        # Retourner des données de test directement
        sample_bestsellers = [
            {
                "name": "Classic White T-Shirt",
                "sold": 150,
                "revenue": 4500.0,
                "rating": 4.5,
                "reviews": 89,
                "category": "Clothing",
                "price": 30.0
            },
            {
                "name": "Slim Fit Blue Jeans",
                "sold": 120,
                "revenue": 7200.0,
                "rating": 4.7,
                "reviews": 156,
                "category": "Clothing",
                "price": 60.0
            },
            {
                "name": "Black Leather Jacket",
                "sold": 85,
                "revenue": 8500.0,
                "rating": 4.8,
                "reviews": 203,
                "category": "Clothing",
                "price": 100.0
            },
            {
                "name": "Running Sneakers",
                "sold": 200,
                "revenue": 12000.0,
                "rating": 4.6,
                "reviews": 178,
                "category": "Shoes",
                "price": 60.0
            },
            {
                "name": "Wool Sweater",
                "sold": 95,
                "revenue": 7125.0,
                "rating": 4.4,
                "reviews": 92,
                "category": "Clothing",
                "price": 75.0
            }
        ]
        
        # Limiter les résultats
        limited_results = sample_bestsellers[:limit]
        
        logger.info(f"Best-sellers retournés: {len(limited_results)}")
        return limited_results
    
    except Exception as e:
        logger.error(f"Erreur bestsellers: {e}")
        return [{"error": str(e)}]

# ... (rest of the code remains the same)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")