
from init_firebase import init
import json


def import_firestore():
    db = init()
    
    # Dicionário para armazenar todas as coleções
    all_data = {}
    
    # Lista de coleções conhecidas (adicione aqui as coleções do seu projeto)
    # Se não souber os nomes, tente acessar o Console do Firebase
    collection_names = [
        "Academia",
        "Banhos",
        "Esportes",
        "Hamburgueria",
        "Hospedagem",
        "Igrejas",
        "Pizzaria",
        "Praças",
        "Restaurantes",
        "Sorveteria",
        "Sushi",
        "Users",
    ]
    
    for collection_name in collection_names:
        try:
            print(f"Carregando coleção: {collection_name}")
            
            # Busca todos os documentos da coleção
            docs = db.collection(collection_name).stream()
            collection_data = []
            
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id  # Adiciona o ID do Firestore ao objeto
                collection_data.append(data)
            
            if collection_data:  # Só adiciona se tiver documentos
                all_data[collection_name] = collection_data
                print(f"  ✓ {len(collection_data)} documentos carregados")
            else:
                print(f"  ⚠ Coleção vazia ou não existe")
                
        except Exception as e:
            print(f"  ✗ Erro ao carregar {collection_name}: {e}")
            continue
    
    # Salva todos os dados no arquivo JSON
    with open("dados.json", "w", encoding="utf-8") as arquivo:
        json.dump(all_data, arquivo, indent=4, ensure_ascii=False)
    
    print(f"\n✅ Total: {len(all_data)} coleções carregadas com sucesso!")
    return f"Dados carregados com sucesso! {len(all_data)} coleções salvas."
