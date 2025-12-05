#!/bin/bash
# Script pour exécuter les commandes GitHub CI en local
# Usage: ./scripts/run_ci_local.sh

set -e  # Arrêter en cas d'erreur

cd "$(dirname "$0")/.." || exit 1

echo "🚀 Exécution des commandes CI en local..."
echo ""

# Couleurs pour l'affichage
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction pour afficher les résultats
print_result() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ $1${NC}"
    else
        echo -e "${RED}❌ $1${NC}"
        exit 1
    fi
}

# 1. LINT & FORMAT CHECK
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  LINT & FORMAT CHECK"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "📝 Vérification du formatage avec Black..."
poetry run black --check . || {
    echo -e "${YELLOW}⚠️  Black a trouvé des fichiers à formater. Exécutez 'poetry run black .' pour les formater.${NC}"
    exit 1
}
print_result "Black check passed"

echo "🔍 Linting avec Ruff..."
poetry run ruff check .
print_result "Ruff check passed"

echo "🔎 Vérification des types avec MyPy..."
poetry run mypy src
print_result "MyPy check passed"

echo ""

# 2. UNIT TESTS
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  UNIT TESTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "🧪 Exécution des tests unitaires avec coverage..."
poetry run pytest tests/unit/ -v --cov=src --cov-report=xml --cov-report=html --cov-report=term
print_result "Unit tests passed"

echo ""

# 3. INTEGRATION TESTS
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  INTEGRATION TESTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${YELLOW}⚠️  Note: Les tests d'intégration nécessitent une base de données PostgreSQL en cours d'exécution.${NC}"
echo -e "${YELLOW}   Assurez-vous que PostgreSQL est démarré et que TEST_DATABASE_URL est configuré.${NC}"
echo ""

echo "🧪 Exécution des tests d'intégration avec coverage..."
poetry run pytest tests/integration/ -v --cov=src --cov-report=xml --cov-report=html --cov-report=term --cov-append
print_result "Integration tests passed"

echo ""

# 4. SECURITY SCANNING
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4️⃣  SECURITY SCANNING"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "🔒 Vérification des vulnérabilités avec Safety..."
poetry export --without-hashes -f requirements.txt -o requirements.txt || true
poetry run safety check --file requirements.txt || {
    echo -e "${YELLOW}⚠️  Safety a trouvé des vulnérabilités potentielles (non bloquant)${NC}"
}
echo "✅ Safety check completed"

echo "🛡️  Analyse de sécurité avec Bandit..."
poetry run bandit -r src -f json -o bandit-report.json || true
poetry run bandit -r src || {
    echo -e "${YELLOW}⚠️  Bandit a trouvé des problèmes de sécurité potentiels (non bloquant)${NC}"
}
echo "✅ Bandit check completed"

echo ""

# 5. MIGRATIONS CHECK
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5️⃣  MIGRATIONS CHECK"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${YELLOW}⚠️  Note: Les migrations nécessitent une base de données PostgreSQL en cours d'exécution.${NC}"
echo ""

echo "📊 Vérification de l'état actuel des migrations..."
poetry run alembic current || {
    echo -e "${YELLOW}⚠️  Impossible de vérifier l'état actuel (base de données peut-être non disponible)${NC}"
}

echo "🔄 Test des migrations (downgrade puis upgrade)..."
if poetry run alembic downgrade -1 2>/dev/null; then
    poetry run alembic upgrade head
    print_result "Migrations check passed"
else
    echo -e "${YELLOW}⚠️  Impossible de tester les migrations (base de données peut-être non disponible)${NC}"
fi

echo ""

# Résumé final
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ Toutes les vérifications CI sont terminées !${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Rapports générés :"
echo "   - Coverage XML: coverage.xml"
echo "   - Coverage HTML: htmlcov/index.html"
echo "   - Security report: bandit-report.json"
echo ""

