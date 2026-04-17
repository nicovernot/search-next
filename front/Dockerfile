FROM node:20-alpine AS builder

WORKDIR /app

COPY front/package.json ./
COPY front/pnpm-lock.yaml ./
RUN npm install -g pnpm && pnpm install --frozen-lockfile

COPY front/. .

ARG NEXT_PUBLIC_API_URL=http://localhost:8003
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}

RUN npm run build

# Dereference pnpm symlinks so Docker COPY doesn't choke on them
RUN cp -rL /app/.next/standalone /app/.next/standalone-resolved

# Production
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production

COPY --from=builder /app/.next/standalone-resolved ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://127.0.0.1:3000/ || exit 1

ENV HOSTNAME="0.0.0.0"
CMD ["node", "server.js"]
