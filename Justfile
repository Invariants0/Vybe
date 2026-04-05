default:
    @just --list

# Start deps (db, redis) + backend & frontend
dev-up:
    docker compose up -d
    overmind start -f Procfile.dev

# Stop everything
dev-down:
    overmind quit || true
    docker compose down

# Start the full monitoring stack too
monitoring-up:
    docker compose --profile monitoring up -d

# Run backend tests
test *args:
    cd backend && pytest {{args}}
