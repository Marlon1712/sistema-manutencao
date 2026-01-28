FROM node:20-slim

WORKDIR /app

# Copia os arquivos de dependências primeiro (otimiza o cache do Docker)
COPY package*.json ./

# Instala as dependências
RUN npm install

# Copia o resto do código
COPY . .

# O Next.js roda na porta 3000 por padrão
EXPOSE 3000

# Comando para rodar em modo desenvolvimento com Hot Reload
CMD ["npm", "run", "dev"]