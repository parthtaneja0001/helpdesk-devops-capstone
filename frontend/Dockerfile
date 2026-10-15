# ---- Stage 1: build the React app ----
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci || npm install
COPY . .
RUN npm run build

# ---- Stage 2: serve static files with unprivileged Nginx ----
FROM nginxinc/nginx-unprivileged:stable-alpine
# Pull in security patches for Alpine packages, then drop back to the non-root user
USER root
RUN apk upgrade --no-cache
USER 101
ENV BACKEND_URL=http://backend:8000
COPY nginx.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 8080
