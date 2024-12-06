from flask import Flask, render_template, request, redirect, url_for, jsonify
import requests
import os

app = Flask(__name__)

# Definindo as variáveis de ambiente
API_BASE_URL = "http://backend:8000"


# Rota para a página inicial
@app.route('/')
def index():
    return render_template('index.html')


# Rota para exibir o formulário de cadastro
@app.route('/cadastro', methods=['GET'])
def inserir_tarefa_form():
    return render_template('cadastro.html')


# Rota para enviar os dados do formulário de cadastro para a API
@app.route('/inserir', methods=['POST'])
def inserir_tarefa():
    try:
        # Captura os dados do formulário
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        done = request.form['done']

        # Converte o valor de 'done' para booleano (a API espera um booleano)
        done_bool = True if done.lower() == 'true' else False

        # Cria o payload para envio
        payload = {
            'titulo': titulo,
            'descricao': descricao,
            'done': done_bool
        }

        # Envia a requisição POST para a API
        response = requests.post(f'{API_BASE_URL}/api/v1/tarefas/', json=payload)
        response.raise_for_status()  # Lança exceção se houver erro HTTP

        # Redireciona para a lista de tarefas se a operação for bem-sucedida
        return redirect(url_for('listar_tarefas'))

    except requests.exceptions.RequestException as e:
        # Log do erro e retorno de mensagem de erro
        print(f"Erro ao inserir tarefa: {e}")
        return "Erro ao inserir tarefa", 500



# Rota para listar todas as tarefas
@app.route('/listar', methods=['GET'])
def listar_tarefas():
    try:
        response = requests.get(f'{API_BASE_URL}/api/v1/tarefas/')
        response.raise_for_status()  # Lança exceção se o status não for 2xx
        tarefas = response.json()
    except (requests.exceptions.RequestException, ValueError) as e:
        print(f"Erro ao obter tarefas: {e}")
        tarefas = []
    return render_template('listar.html', tarefas=tarefas)


# Rota para exibir edição de tarefa
@app.route('/atualizar/<int:tarefa_id>', methods=['GET'])
def atualizar_tarefa_form(tarefa_id):
    response = requests.get(f"{API_BASE_URL}/api/v1/tarefas/")
    # filtrando apenas o livro correspondente ao ID
    tarefas = [tarefa for tarefa in response.json() if tarefa['id'] == tarefa_id]
    if len(tarefas) == 0:
        return "tarefa não encontrado", 404
    tarefa = tarefas[0]
    return render_template('atualizar.html', tarefa=tarefa)


# Rota para enviar os dados do formulário de edição de tarefa para a API
@app.route('/atualizar/<int:tarefa_id>', methods=['POST'])
def atualizar_tarefa(tarefa_id):
    titulo = request.form['titulo']
    descricao = request.form['descricao']
    done = request.form['done'] == 'true'  # Converte a string 'true'/'false' para boolean

    payload = {
        'titulo': titulo,
        'descricao': descricao,
        'done': done
    }

    response = requests.patch(f"{API_BASE_URL}/api/v1/tarefas/{tarefa_id}", json=payload)

    if response.status_code == 200:
        return redirect(url_for('listar_tarefas'))
    else:
        return "Erro ao atualizar tarefa", 500


# Rota para excluir tarefa
@app.route('/excluir/<int:tarefa_id>', methods=['POST'])
def excluir_tarefa(tarefa_id):
    response = requests.delete(f"{API_BASE_URL}/api/v1/tarefas/{tarefa_id}")

    if response.status_code == 200:
        return redirect(url_for('listar_tarefas'))
    else:
        return "Erro ao excluir tarefa", 500


# Rota para resetar o database
@app.route('/confirmacao', methods=['GET'])
def resetar_database():
    response = requests.delete(f"{API_BASE_URL}/api/v1/tarefas/")

    if response.status_code == 200:
        return render_template('confirmacao.html')
    else:
        return "Erro ao resetar o database", 500


if __name__ == '__main__':
    app.run(debug=True, port=3000, host='0.0.0.0')
