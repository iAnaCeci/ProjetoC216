-- Remover a tabela "tarefas" caso ela exista
DROP TABLE IF EXISTS "tarefas";

-- Criar a tabela "tarefas"
CREATE TABLE "tarefas" (
    "id" SERIAL PRIMARY KEY,
    "titulo" VARCHAR(255) NOT NULL,
    "descricao" VARCHAR(255) NOT NULL,
    "done" BOOLEAN NOT NULL DEFAULT FALSE
);

-- Inserir tarefas
INSERT INTO "tarefas" ("titulo", "descricao", "done")
VALUES ('Estudar Flask', 'Revisar conceitos e criar um projeto simples com Flask', FALSE);

INSERT INTO "tarefas" ("titulo", "descricao", "done")
VALUES ('Finalizar artigo acadêmico', 'Escrever a conclusão e revisar o texto', FALSE);

INSERT INTO "tarefas" ("titulo", "descricao", "done")
VALUES ('Organizar reunião de projeto', 'Agendar reunião com a equipe e preparar pauta', TRUE);
