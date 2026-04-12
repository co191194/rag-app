FROM node:24-slim

WORKDIR /app

# Corepackを有効化してpnpmを利用可能にする
RUN corepack enable && corepack prepare pnpm@latest --activate

COPY package.json pnpm-lock.yaml ./

RUN pnpm install

CMD ["pnpm", "run", "dev", "--host", "0.0.0.0"]