FROM node:20-slim

WORKDIR /app

# Copia os arquivos de dependência
COPY package*.json ./

# Instala as dependências (dentro do container)
RUN npm install

# Copia o restante dos arquivos
COPY . .

# Expõe a porta do Next.js
EXPOSE 3000

# Comando para rodar em modo desenvolvimento
CMD ["npm", "run", "dev"]