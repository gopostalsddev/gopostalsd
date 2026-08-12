FROM node:20.19.0-bookworm-slim AS build

WORKDIR /build
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
ARG VITE_API_BASE_URL=/api
ARG VITE_SQUARE_ENVIRONMENT=sandbox
ARG VITE_SQUARE_APPLICATION_ID=sandbox-sq0idb-rehearsal-placeholder
ARG VITE_SQUARE_LOCATION_ID=rehearsal-placeholder
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL \
    VITE_SQUARE_ENVIRONMENT=$VITE_SQUARE_ENVIRONMENT \
    VITE_SQUARE_APPLICATION_ID=$VITE_SQUARE_APPLICATION_ID \
    VITE_SQUARE_LOCATION_ID=$VITE_SQUARE_LOCATION_ID
RUN npm run build

FROM nginxinc/nginx-unprivileged:1.27.5-alpine
COPY --from=build /build/dist /usr/share/nginx/html
COPY <<'EOF' /etc/nginx/conf.d/default.conf
server {
    listen 8080;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;

    location /api/ {
        proxy_pass http://web:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /health/ {
        proxy_pass http://web:5000;
        proxy_set_header Host $host;
    }

    location / {
        try_files $uri $uri/ /index.html;
    }
}
EOF
LABEL com.docker.compose.project="gopostal-rehearsal"
