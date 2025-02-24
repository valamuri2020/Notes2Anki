# Build stage
FROM node:22.9.0-slim AS build

WORKDIR /app

# Copy package files and install dependencies
COPY package.json package-lock.json ./
RUN npm ci

# Copy source code and build the app
COPY . .
RUN npm run build

# Production stage
FROM node:22.9.0-slim AS prod

WORKDIR /app

# Copy built files
COPY --from=build /app ./

# Expose Next.js default port
EXPOSE 3000

# Start Next.js in production mode
CMD ["npm", "run", "start"]
