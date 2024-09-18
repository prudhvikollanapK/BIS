FROM mcr.microsoft.com/playwright:v1.28.0-focal

WORKDIR /app

RUN corepack enable && npm cache clean --force

COPY ./package.json ./package-lock.json /app/

RUN rm -rf node_modules package-lock.json

RUN npm cache clean --force

RUN npm install

RUN npx playwright install

COPY script.js /app/

ENV BLOCKED_DOMAINS='[]'

CMD ["node", "/app/script.js"]
