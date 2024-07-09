import os
import json
import threading
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Nome do arquivo para armazenar os dados
DATA_FILE = 'data.json'
lock = threading.Lock()

# Função para carregar dados do arquivo JSON
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError:
            print("Erro ao decodificar o arquivo JSON")
            return initialize_default_data()
    return initialize_default_data()

# Função para inicializar dados padrão
def initialize_default_data():
    return {
        "cortes": [
            {"id": 1, "nome": "Militar", "preco": "R$10"},
            {"id": 2, "nome": "Social", "preco": "R$15"},
            {"id": 3, "nome": "Degradê", "preco": "R$30"},
            {"id": 4, "nome": "Feminino", "preco": "R$40"}
        ],
        "barbas": [
            {"id": 1, "nome": "Simples", "preco": "R$10"},
            {"id": 2, "nome": "Desenhada", "preco": "R$30"},
            {"id": 3, "nome": "Completa", "preco": "R$35"}
        ],
        "outrosServicos": [
            {"id": 1, "nome": "Design de sobrancelhas", "preco": "R$20"},
            {"id": 2, "nome": "Limpeza de sobrancelhas", "preco": "R$25"}
        ]
    }

# Função para salvar dados no arquivo JSON
def save_data(data):
    with lock:
        try:
            with open(DATA_FILE, 'w') as file:
                json.dump(data, file)
            print(f"Dados salvos: {data}")
        except IOError:
            print("Erro ao salvar o arquivo JSON")

# Carregar dados na memória
data = load_data()

@app.before_first_request
def initialize_data():
    global data
    data = load_data()
    print(f"Dados carregados na inicialização: {data}")

def get_item(service_type, item_id):
    for item in data[service_type]:
        if item['id'] == item_id:
            return item
    return None

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico')

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "message": "Bem-vindo à API de Serviços!",
        "endpoints": ["/cortes", "/barbas", "/outrosServicos"]
    })

@app.route('/<service_type>', methods=['GET'])
def get_all(service_type):
    try:
        if service_type not in data:
            return jsonify({"error": "Serviço não encontrado"}), 404
        return jsonify(data.get(service_type, []))
    except Exception as e:
        print(f"Erro ao obter todos os itens de {service_type}: {e}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@app.route('/<service_type>/<int:item_id>', methods=['GET'])
def get_one(service_type, item_id):
    try:
        if service_type not in data:
            return jsonify({"error": "Serviço não encontrado"}), 404
        item = get_item(service_type, item_id)
        if item:
            return jsonify(item)
        return jsonify({"error": "Item não encontrado"}), 404
    except Exception as e:
        print(f"Erro ao obter o item {item_id} de {service_type}: {e}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@app.route('/<service_type>', methods=['POST'])
def create(service_type):
    try:
        if service_type not in data:
            return jsonify({"error": "Serviço não encontrado"}), 404
        item = request.json
        item['id'] = max([i['id'] for i in data[service_type]] or [0]) + 1
        data[service_type].append(item)
        save_data(data)  # Salvar dados após adicionar novo item
        print(f"Novo item adicionado em {service_type}: {item}")  # Log para depuração
        return jsonify(item), 201
    except Exception as e:
        print(f"Erro ao criar um novo item em {service_type}: {e}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@app.route('/<service_type>/<int:item_id>', methods=['PUT'])
def update(service_type, item_id):
    try:
        if service_type not in data:
            return jsonify({"error": "Serviço não encontrado"}), 404
        item = get_item(service_type, item_id)
        if item:
            for key, value in request.json.items():
                item[key] = value
            save_data(data)  # Salvar dados após atualização
            return jsonify(item)
        return jsonify({"error": "Item não encontrado"}), 404
    except Exception as e:
        print(f"Erro ao atualizar o item {item_id} em {service_type}: {e}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@app.route('/<service_type>/<int:item_id>', methods=['DELETE'])
def delete(service_type, item_id):
    try:
        if service_type not in data:
            return jsonify({"error": "Serviço não encontrado"}), 404
        item = get_item(service_type, item_id)
        if item:
            data[service_type].remove(item)
            save_data(data)  # Salvar dados após deletar item
            return jsonify({"message": "Item deletado com sucesso"})
        return jsonify({"error": "Item não encontrado"}), 404
    except Exception as e:
        print(f"Erro ao deletar o item {item_id} de {service_type}: {e}")
        return jsonify({"error": "Erro interno do servidor"}), 500

if __name__ == '__main__':
    app.run(debug=True)
