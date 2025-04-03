# Use a imagem base do Python
FROM python:3.10.12

# Defina o diretório de trabalho
WORKDIR /app

# Copie o arquivo requirements.txt para dentro do container
COPY requirements.txt .

# Instale as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copie os arquivos do projeto para dentro do container
COPY . .

# Exponha a porta, caso necessário
EXPOSE 8080

# Comando padrão para rodar a aplicação
CMD ["python", "app.py"]  # Altere conforme necessário
