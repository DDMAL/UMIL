# Frontend tests (Vitest)
test-frontend:
	docker compose exec app npm test --prefix /virtual-instrument-museum/frontend

.PHONY: test-frontend

