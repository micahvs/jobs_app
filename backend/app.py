from application import create_app
from flask import Flask, request, jsonify
from flask_cors import CORS

app = create_app()

# Allow CORS for React frontend
CORS(app, supports_credentials=True, origins="http://localhost:3000")



@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    return jsonify({"message": "User registered!", "data": data})

if __name__ == '__main__':
    app.run(port=5000, debug=True)

print("Registered Routes:")
for rule in app.url_map.iter_rules():
    print(f"{rule.methods} {rule.rule}")