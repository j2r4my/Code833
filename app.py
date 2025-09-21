import json
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Nom du fichier de données
PRICES_FILE = 'prices.json'


def load_data(filepath):
    """Charge les données de prix à partir d'un fichier JSON."""
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            data = json.load(file)
        for item in data:
            item['store_cession_price'] = float(item['store_cession_price'])
            item['sales_price'] = float(item['sales_price'])
        return data
    except (FileNotFoundError, ValueError) as e:
        print(f"Erreur lors du chargement des données : {e}")
        return None


# Chargement des données au démarrage
all_prices = load_data(PRICES_FILE)


def find_closest_prices(data, store_cession_price):
    """Recherche le Sales Price et le code Item les plus proches."""
    try:
        price_to_find = float(store_cession_price)
    except ValueError:
        return None, None, None

    closest_item = None
    min_difference = float('inf')

    for item in data:
        current_price = item['store_cession_price']
        difference = abs(current_price - price_to_find)

        if difference < min_difference:
            min_difference = difference
            closest_item = item

    if closest_item:
        return (closest_item['sales_price'],
                closest_item['item'],
                closest_item['store_cession_price'])
    return None, None, None


@app.route('/')
def index():
    """Route principale pour afficher la page HTML."""
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search_prices():
    """Route API pour la recherche de prix."""
    user_input = request.json.get('price')

    if not all_prices:
        return jsonify({'error': 'Erreur de chargement des données'}), 500

    if not user_input or not user_input.strip():
        return jsonify({'error': 'Veuillez entrer un prix.'}), 400

    # Normalisation de l'entrée utilisateur
    normalized_input = user_input.replace(',', '.')

    sales_price, item_code, closest_cession_price = find_closest_prices(all_prices, normalized_input)

    if sales_price is not None:
        return jsonify({
            'success': True,
            'closest_cession_price': closest_cession_price,
            'sales_price': sales_price,
            'item_code': item_code
        })
    else:
        return jsonify({'error': 'Veuillez entrer un nombre valide.'}), 400


if __name__ == '__main__':
    app.run(debug=True)
