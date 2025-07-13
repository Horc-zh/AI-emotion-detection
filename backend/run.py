from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)


# curl -X POST http://localhost:5000/api/chat/ -H "Content-Type: application/json" -d "{\"message\": \"你好\"}"

