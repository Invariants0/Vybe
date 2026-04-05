# Multi-stage build for Next.js frontend with Bun
FROM oven/bun:1-alpine AS builder

WORKDIR /app

ENV NEXT_TELEMETRY_DISABLED=1

# Copy Bun dependency manifest
COPY frontend/package.json frontend/bun.lock* ./

# Install dependencies from Bun lockfile
RUN bun install --frozen-lockfile

# Copy source code
COPY frontend ./

# Ensure public directory exists (Next.js requires it)
RUN mkdir -p public

# Build Next.js application
RUN bun run build

# Production runtime stage
FROM oven/bun:1-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV HOSTNAME=0.0.0.0
ENV PORT=3000

RUN apk add --no-cache curl nodejs

# Create non-root user (using UID/GID 1001 to avoid conflicts with bun user)
RUN addgroup -g 1001 nextjs && adduser -u 1001 -G nextjs -s /bin/sh -D nextjs

# Copy standalone output (Next.js standalone mode)
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

# Set ownership
RUN chown -R nextjs:nextjs /app

USER nextjs

EXPOSE 3000


CMD ["node", "server.js"]
