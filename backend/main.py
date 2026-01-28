from fastapi import FastAPI, UploadFile, File, HTTPException
import fitz  # PyMuPDF
from langchain_text_splitters import RecursiveCharacterTextSplitter
import psycopg2
from psycopg2.extras import execute_values
import requests
import json

app = FastAPI()

# Configurações
DB_PARAMS = "host=db dbname=gestao_manutencao user=admin password=automacao@2025"
OLLAMA_URL = "http://ollama:11434/api/embeddings"

def get_embedding(text):
    """Chama o Ollama para transformar texto em um vetor numérico"""
    payload = {"model": "llama3", "prompt": text}
    response = requests.post(OLLAMA_URL, json=payload)
    return response.json()["embedding"]

@app.post("/ingerir-manual")
async def ingerir_manual(file: UploadFile = File(...)):
    try:
        # 1. Ler o PDF
        pdf_content = await file.read()
        doc = fitz.open(stream=pdf_content, filetype="pdf")
        texto_completo = ""
        for page in doc:
            texto_completo += page.get_text()

        # 2. Quebrar em pedaços menores (Chunks)
        # Isso ajuda a IA a não se perder em manuais gigantes
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = text_splitter.split_text(texto_completo)

        # 3. Gerar Vetores e Salvar no Banco
        conn = psycopg2.connect(DB_PARAMS)
        cur = conn.cursor()
        
        for chunk in chunks:
            vector = get_embedding(chunk)
            cur.execute(
                "INSERT INTO procedimentos (titulo, tipo, conteudo_json, embedding, status) VALUES (%s, %s, %s, %s, %s)",
                (file.filename, "MANUAL", json.dumps({"texto": chunk}), vector, "publicado")
            )
        
        conn.commit()
        cur.close()
        conn.close()
        
        return {"status": f"Manual {file.filename} processado em {len(chunks)} partes."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/buscar")
async def buscar_conhecimento(pergunta: str):
    """Busca semântica: encontra os trechos mais relevantes para a dúvida"""
    pergunta_vector = get_embedding(pergunta)
    
    conn = psycopg2.connect(DB_PARAMS)
    cur = conn.cursor()
    
    # Busca por similaridade de cosseno (<=>) usando PGVector
    cur.execute("""
        SELECT conteudo_json->>'texto' as trecho, titulo
        FROM procedimentos 
        ORDER BY embedding <=> %s::vector 
        LIMIT 3
    """, (pergunta_vector,))
    
    resultados = cur.fetchall()
    cur.close()
    conn.close()
    
    return {"resultados": [{"texto": r[0], "fonte": r[1]} for r in resultados]}