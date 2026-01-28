from firebase import db
import json


def upload_to_firestore():
    """
    Envia os dados reorganizados para o Firestore em lote.
    Cria 3 coleções: cat_locations, users e locations
    """
    db_client = db()
    
    print("📦 Carregando dados reorganizados...\n")
    
    with open("dados-reorganizados.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # ==================== UPLOAD cat_locations ====================
    print("📁 Enviando categorias para cat_locations...")
    batch = db_client.batch()
    count = 0
    
    for category in data["cat_locations"]:
        cat_id = category["id"]
        cat_ref = db_client.collection("cat_locations").document(cat_id)
        batch.set(cat_ref, {
            "nome": category["nome"],
            "descricao": category["descricao"]
        })
        count += 1
        print(f"  ✓ Preparado: {category['nome']}")
    
    batch.commit()
    print(f"✅ {count} categorias enviadas!\n")
    
    # ==================== UPLOAD users ====================
    print("👥 Enviando usuários para users...")
    batch = db_client.batch()
    count = 0
    
    for user in data["users"]:
        user_id = user["id"]
        user_ref = db_client.collection("users").document(user_id)
        batch.set(user_ref, {
            "name": user["name"],
            "email": user["email"],
            "password": user["password"],
            "online": user["online"]
        })
        count += 1
        print(f"  ✓ Preparado: {user['name']}")
    
    batch.commit()
    print(f"✅ {count} usuários enviados!\n")
    
    # ==================== UPLOAD locations ====================
    print("📍 Enviando locais para locations...")
    batch = db_client.batch()
    # Processa em lotes de 500 (limite do Firestore)
    locations = data["locations"]
    batch_size = 500
    total = len(locations)
    
    for i in range(0, total, batch_size):
        batch = db_client.batch()
        batch_locations = locations[i:i + batch_size]
        
        for location in batch_locations:
            loc_id = location["id"]
            loc_ref = db_client.collection("locations").document(loc_id)
            
            # Cria referências para categoria e usuário
            category_ref = db_client.collection("cat_locations").document(location["category_ref"])
            user_ref = db_client.collection("users").document(location["user_ref"])
            
            batch.set(loc_ref, {
                "nome": location["nome"],
                "descricao_curta": location["descricao_curta"],
                "descricao_longa": location["descricao_longa"],
                "imagem": location["imagem"],
                "telefone": location["telefone"],
                "avaliacoes": location["avaliacoes"],
                "opcoes_servico": location["opcoes_servico"],
                "endereco": location["endereco"],
                "category_ref": category_ref,
                "user_ref": user_ref
            })
            print(f"  ✓ Preparado: {location['nome']}")
        
        batch.commit()
        print(f"  💾 Lote {i//batch_size + 1} enviado ({len(batch_locations)} locais)")
    
    print(f"✅ {total} locais enviados!\n")
    
    # ==================== RESUMO ====================
    print("=" * 60)
    print("🎉 UPLOAD CONCLUÍDO!")
    print("=" * 60)
    print(f"\n📊 Dados enviados ao Firestore:")
    print(f"  • cat_locations: {len(data['cat_locations'])} categorias")
    print(f"  • users: {len(data['users'])} usuários")
    print(f"  • locations: {len(data['locations'])} locais")
    print("\n✅ Acesse o Console do Firebase para verificar os dados")
    print("=" * 60)
    
    return "Upload concluído com sucesso!"


if __name__ == "__main__":
    upload_to_firestore()
