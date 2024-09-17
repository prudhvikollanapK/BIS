# Use a base image with Node.js
FROM node:18

# Install dependencies required by Puppeteer
RUN apt-get update && \
    apt-get install -y \
    wget \
    ca-certificates \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libxss1 \
    libxtst6 \
    libnss3 \
    libnspr4 \
    libgbm1 \
    libu2f-udev \
    libdrm2 \
    lsb-release \
    libxkbcommon0 \
    libnss3-tools \
    xvfb \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the Puppeteer script into the image
COPY script.js /app/script.js

# Install Puppeteer
RUN npm install puppeteer@latest --legacy-peer-deps

# Expose the port your application listens on
EXPOSE 3000

# Set environment variable for blocked domains
ENV BLOCKED_DOMAINS='[]'

# Run the Puppeteer script
CMD ["sh", "-c", "Xvfb :99 -screen 0 1280x1024x24 & node /app/script.js"]
