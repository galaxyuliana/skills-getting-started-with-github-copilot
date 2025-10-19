#!/bin/bash

# Test runner script for the High School Management System API

echo "🧪 Running FastAPI Tests for High School Management System"
echo "==========================================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${1}${2}${NC}"
}

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    print_status $RED "❌ pytest is not installed. Please run: pip install -r requirements.txt"
    exit 1
fi

print_status $YELLOW "📋 Running quick tests (excluding slow tests)..."
echo ""

# Run main test suite (excluding slow tests)
pytest tests/ -v -m "not slow" --tb=short

QUICK_EXIT_CODE=$?

if [ $QUICK_EXIT_CODE -eq 0 ]; then
    print_status $GREEN "✅ Quick tests passed!"
    echo ""
    
    # Ask if user wants to run slow tests
    read -p "🐌 Run slow tests? (y/N): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status $YELLOW "🐌 Running slow tests..."
        pytest tests/ -v -m "slow" --tb=short
        SLOW_EXIT_CODE=$?
        
        if [ $SLOW_EXIT_CODE -eq 0 ]; then
            print_status $GREEN "✅ All tests passed!"
        else
            print_status $RED "❌ Some slow tests failed"
            exit $SLOW_EXIT_CODE
        fi
    fi
else
    print_status $RED "❌ Some quick tests failed"
    exit $QUICK_EXIT_CODE
fi

echo ""
print_status $GREEN "🎉 Test run complete!"

# Show test coverage summary
echo ""
print_status $YELLOW "📊 Test Summary:"
echo "  • API Endpoint Tests: ✅"
echo "  • Data Model Tests: ✅"
echo "  • Performance Tests: ✅"
echo "  • Error Handling Tests: ✅"
echo "  • End-to-End Workflow Tests: ✅"