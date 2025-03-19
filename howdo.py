from flask import Flask, request

app = Flask(__name__)

@app.route('/start', methods=['POST'])
def handle_start():
    print("Получен запрос:", request.json)  # Логи для проверки запроса
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
