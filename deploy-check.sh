#!/bin/bash
# Production Deployment Verification Script
# Run this before deploying to production

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     PRODUCTION DEPLOYMENT READINESS CHECK                     ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

checks_passed=0
checks_failed=0

# Function to print test results
check_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
        ((checks_passed++))
    else
        echo -e "${RED}❌ $2${NC}"
        ((checks_failed++))
    fi
}

# 1. Check Python version
echo "🔍 Checking Python environment..."
python --version > /dev/null 2>&1
check_result $? "Python installed"

# 2. Check virtual environment
if [ -d "venv" ]; then
    echo -e "${GREEN}✅ Virtual environment found${NC}"
    ((checks_passed++))
else
    echo -e "${YELLOW}⚠️  Virtual environment not found (create with: python -m venv venv)${NC}"
    ((checks_failed++))
fi

# 3. Check required files
echo ""
echo "🔍 Checking project structure..."
required_files=(
    "app/main.py"
    "requirements.txt"
    ".env.example"
    "docker-compose.yml"
    "Dockerfile"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ Found $file${NC}"
        ((checks_passed++))
    else
        echo -e "${RED}❌ Missing $file${NC}"
        ((checks_failed++))
    fi
done

# 4. Check .env configuration
echo ""
echo "🔍 Checking environment configuration..."
if [ -f ".env" ]; then
    echo -e "${GREEN}✅ .env file exists${NC}"
    ((checks_passed++))
    
    # Check for essential variables
    essential_vars=("DATABASE_URL" "JWT_SECRET_KEY" "API_PORT")
    for var in "${essential_vars[@]}"; do
        if grep -q "$var" .env; then
            echo -e "${GREEN}✅ $var configured${NC}"
            ((checks_passed++))
        else
            echo -e "${YELLOW}⚠️  $var not configured in .env${NC}"
            ((checks_failed++))
        fi
    done
else
    echo -e "${YELLOW}⚠️  .env file not found (copy from .env.example)${NC}"
    ((checks_failed++))
fi

# 5. Check dependencies
echo ""
echo "🔍 Checking dependencies..."
if [ -f "requirements.txt" ]; then
    echo -e "${GREEN}✅ requirements.txt exists${NC}"
    ((checks_passed++))
    
    # Count dependencies
    dep_count=$(grep -c "^" requirements.txt || true)
    echo "   Found $dep_count dependencies"
else
    echo -e "${RED}❌ requirements.txt missing${NC}"
    ((checks_failed++))
fi

# 6. Check database setup
echo ""
echo "🔍 Checking database setup..."
if [ -f "scripts/init_db.py" ]; then
    echo -e "${GREEN}✅ Database initialization script found${NC}"
    ((checks_passed++))
else
    echo -e "${RED}❌ Database initialization script missing${NC}"
    ((checks_failed++))
fi

# 7. Check Docker setup
echo ""
echo "🔍 Checking Docker setup..."
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✅ Docker installed${NC}"
    ((checks_passed++))
    
    if command -v docker-compose &> /dev/null; then
        echo -e "${GREEN}✅ Docker Compose installed${NC}"
        ((checks_passed++))
    else
        echo -e "${YELLOW}⚠️  Docker Compose not installed${NC}"
        ((checks_failed++))
    fi
else
    echo -e "${YELLOW}⚠️  Docker not installed (required for containerized deployment)${NC}"
    ((checks_failed++))
fi

# 8. Check documentation
echo ""
echo "🔍 Checking documentation..."
docs=(
    "README.md"
    "DEPLOYMENT.md"
    "API_GUIDE.md"
)

for doc in "${docs[@]}"; do
    if [ -f "$doc" ]; then
        echo -e "${GREEN}✅ Found $doc${NC}"
        ((checks_passed++))
    else
        echo -e "${YELLOW}⚠️  Missing $doc${NC}"
        ((checks_failed++))
    fi
done

# Summary
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    DEPLOYMENT READINESS SUMMARY                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}Passed: $checks_passed${NC}"
echo -e "${RED}Failed: $checks_failed${NC}"
echo ""

if [ $checks_failed -eq 0 ]; then
    echo -e "${GREEN}✅ SYSTEM IS DEPLOYMENT READY!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Review .env configuration"
    echo "2. Run: python scripts/init_db.py"
    echo "3. Run: python scripts/train_model.py (optional)"
    echo "4. Deploy with: docker-compose up -d"
    exit 0
else
    echo -e "${YELLOW}⚠️  PLEASE FIX THE ABOVE ISSUES BEFORE DEPLOYING${NC}"
    exit 1
fi
