from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional
import time
import asyncpg
import os

# Função para obter a conexão com o banco de dados PostgreSQL
async def get_database():
    DATABASE_URL = os.environ.get("PGURL", "postgres://postgres:postgres@db:5432/tarefas")
    return await asyncpg.connect(DATABASE_URL)

# Inicializar a aplicação FastAPI
app = FastAPI()

# Modelo para adicionar novos livros
class Tarefa(BaseModel):
    id: Optional[int] = None
    titulo: str
    descricao: str
    done: bool

class TarefaBase(BaseModel):
    titulo: str
    descricao: str
    done: bool



# Modelo para atualizar atributos de uma tarefa(exceto o ID)
class AtualizarTarefa(BaseModel):
    titulo: Optional[str] = None
    descricao: Optional[str] = None
    done: Optional[int] = None

# Middleware para logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    print(f"Path: {request.url.path}, Method: {request.method}, Process Time: {process_time:.4f}s")
    return response


# 1. Adicionar uma tarefa
@app.post("/api/v1/tarefas/", status_code=201)
async def adicionar_tarefa(tarefa: TarefaBase):
    try:
        conn = await get_database()
        query = "INSERT INTO tarefas (titulo, descricao, done) VALUES ($1, $2, $3)"
        async with conn.transaction():
            result = await conn.execute(query, tarefa.titulo, tarefa.descricao, tarefa.done)
            return {"message": "Tarefa adicionada com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao adicionar a tarefa: {str(e)}")
    finally:
        await conn.close()


# 2. Listar todos as tarefas
@app.get("/api/v1/tarefas/", response_model=List[Tarefa])
async def listar_tarefas():
    conn = await get_database()
    try:
        # Buscar todos tarefas no banco de dados
        query = "SELECT * FROM tarefas"
        rows = await conn.fetch(query)
        tarefas = [dict(row) for row in rows]
        return tarefas
    finally:
        await conn.close()

# 3. Buscar tarefas por ID
@app.get("/api/v1/tarefas/{tarefa_id}")
async def listar_tarefa_por_id(tarefa_id: int):
    conn = await get_database()
    try:
        # Buscar tarefa por ID
        query = "SELECT * FROM tarefas WHERE id = $1"
        tarefa = await conn.fetchrow(query, tarefa_id)
        if tarefa is None:
            raise HTTPException(status_code=404, detail="Tarefa não encontrado.")
        return dict(tarefa)
    finally:
        await conn.close()

# 5. Atualizar atributos de uma tarefa pelo ID (exceto o ID)
@app.patch("/api/v1/tarefas/{tarefa_id}", response_model=TarefaBase)
async def atualizar_tarefa(tarefa_id: int, tarefa: TarefaBase):
    conn = await get_database()
    query = """
        UPDATE tarefas
        SET titulo = $1, descricao = $2, done = $3
        WHERE id = $4
        RETURNING id, titulo, descricao, done
    """
    try:
        # Converte o valor de 'done' para boolean
        done_bool = bool(tarefa.done)
        async with conn.transaction():
            result = await conn.fetchrow(query, tarefa.titulo, tarefa.descricao, done_bool, tarefa_id)
            if not result:
                raise HTTPException(status_code=404, detail="Tarefa não encontrada")
            return TarefaBase(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar a tarefa: {str(e)}")
    finally:
        await conn.close()


# 6. Remover uma tarefa pelo ID
@app.delete("/api/v1/tarefas/{tarefa_id}")
async def remover_tarefa(tarefa_id: int):
    conn = await get_database()
    try:
        # Verificar se tarefa existe
        query = "SELECT * FROM tarefas WHERE id = $1"
        tarefa = await conn.fetchrow(query, tarefa_id)
        if tarefa is None:
            raise HTTPException(status_code=404, detail="Tarefa não encontrada.")

        # Remover tarefa do banco de dados
        delete_query = "DELETE FROM tarefas WHERE id = $1"
        await conn.execute(delete_query, tarefa_id)
        return {"message": "Tarefa removido com sucesso!"}
    finally:
        await conn.close()

# 7. Resetar repositorio tarefa
@app.delete("/api/v1/tarefas/")
async def resetar_tarefa():
    init_sql = os.getenv("INIT_SQL", "db/init.sql")
    conn = await get_database()
    try:
        # Read SQL file contents
        with open(init_sql, 'r') as file:
            sql_commands = file.read()
        # Execute SQL commands
        await conn.execute(sql_commands)
        return {"message": "Banco de dados limpo com sucesso!!"}
    finally:
        await conn.close()


