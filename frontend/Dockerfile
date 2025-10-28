FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies with increased timeout and force resolution
RUN npm install --legacy-peer-deps --fetch-timeout=600000 && \
    npm install ajv@^7.0.0 --legacy-peer-deps --save-dev

# Copy application code
COPY . .

# Expose port
EXPOSE 3000

# Start development server
CMD ["npm", "start"]
