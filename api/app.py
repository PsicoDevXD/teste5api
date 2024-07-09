import os
import json
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Nome do arquivo para armazenar os dados
DATA_FILE = 'data.json'

# Função para carregar dados do arquivo JSON
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as file:
            return json.load(file)
    return {
        "cortes": [
            {"id": 1, "nome": "Militar", "preco": "R$10"},
            {"id": 2, "nome": "Social", "preco": "R$15"},
            {"id": 3, "nome": "Degradê", "preco": "R$30"},
            {"id": 4, "nome": "Feminino", "preco": "R$40"},
            {"id": 5, "nome": "Luzes", "preco": "R$80"}
        ],
        "barbas": [
            {"id": 1, "nome": "Simples", "preco": "R$10"},
            {"id": 2, "nome": "Desenhada", "preco": "R$30"},
            {"id": 3, "nome": "Completa", "preco": "R$35"}
        ],
        "outrosservicos": [
            {"id": 1, "nome": "Design de sobrancelhas", "preco": "R$20"},
            {"id": 2, "nome": "Limpeza de sobrancelhas", "preco": "R$25"}
        ]
    }

# Função para salvar dados no arquivo JSON
def save_data(data):
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file)

# Carregar dados na memória
data = load_data()

def get_item(service_type, item_id):
    for item in data[service_type]:
        if item['id'] == item_id:
            return item
    return None

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "message": "Bem-vindo à API de Serviços!",
        "endpoints": ["/cortes", "/barbas", "/outrosServicos"]
    })

@app.route('/<service_type>', methods=['GET'])
def get_all(service_type):
    return jsonify(data.get(service_type, []))

@app.route('/<service_type>/<int:item_id>', methods=['GET'])
def get_one(service_type, item_id):
    item = get_item(service_type, item_id)
    if item:
        return jsonify(item)
    return jsonify({"error": "Item não encontrado"}), 404

@app.route('/<service_type>', methods=['POST'])
def create(service_type):
    item = request.json
    item['id'] = max([i['id'] for i in data[service_type]] or [0]) + 1
    data[service_type].append(item)
    save_data(data)  # Salvar dados após adicionar novo item
    print(f"Novo item adicionado em {service_type}: {item}")  # Log para depuração
    return jsonify(item), 201

@app.route('/<service_type>/<int:item_id>', methods=['PUT'])
def update(service_type, item_id):
    item = get_item(service_type, item_id)
    if item:
        for key, value in request.json.items():
            item[key] = value
        save_data(data)  # Salvar dados após atualização
        return jsonify(item)
    return jsonify({"error": "Item não encontrado"}), 404

@app.route('/<service_type>/<int:item_id>', methods=['DELETE'])
def delete(service_type, item_id):
    item = get_item(service_type, item_id)
    if item:
        data[service_type].remove(item)
        save_data(data)  # Salvar dados após deletar item
        return jsonify({"message": "Item deletado com sucesso"})
    return jsonify({"error": "Item não encontrado"}), 404

if __name__ == '__main__':
    app.run(debug=True)


if __name__ == '__main__':
    app.run(debug=True)
