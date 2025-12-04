# Stage 1: Build
FROM node:20-alpine AS builder

# Install pnpm
RUN npm install -g pnpm@10.14.0

WORKDIR /app

# Copy workspace root package files first
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY angular.json tsconfig.json ./

# Copy library package.json if it exists (for dependency resolution)
# Note: Angular apps in workspace use root package.json, so no need to copy app1/package.json
COPY libraries/shared-ui/package.json ./libraries/shared-ui/

# Install all workspace dependencies
RUN pnpm install --frozen-lockfile

# Copy all source code (workspace root and all projects)
COPY . .

# Build the application from workspace root
# Angular workspace outputs to dist/app1/browser
RUN pnpm exec ng build app1 --configuration production

# Stage 2: Serve with nginx
FROM nginx:alpine

# Copy built assets from workspace build output
COPY --from=builder /app/dist/app1/browser /usr/share/nginx/html

# Copy nginx configuration
RUN echo 'server { \
    listen 80; \
    server_name localhost; \
    root /usr/share/nginx/html; \
    index index.html; \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ { \
        expires 1y; \
        add_header Cache-Control "public, immutable"; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
