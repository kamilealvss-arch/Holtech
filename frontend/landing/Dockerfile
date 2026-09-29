# Estágio 1: Build
FROM node:22-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Estágio 2: Nginx para servir os arquivos estáticos
FROM nginx:alpine

# Copia os arquivos compilados do Nitro/Nuxt
COPY --from=builder /app/.output/public /usr/share/nginx/html

# Configuração tratando subpastas estáticas e evitando o loop 500
RUN echo 'server { \
    listen 4173; \
    root /usr/share/nginx/html; \
    index index.html index.htm; \
    \
    location / { \
        try_files $uri $uri/ $uri/index.html =404; \
    } \
    \
    location = /favicon.ico { \
        log_not_found off; \
        access_log off; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 4173

CMD ["nginx", "-g", "daemon off;"]