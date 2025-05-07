#!/bin/bash
# QuickTARA Test Runner
# This script allows running all tests or tests for specific components

set -e  # Exit immediately if a command exits with a non-zero status

# Set colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${YELLOW}QuickTARA Test Runner${NC}"
echo "======================="

function run_test_file() {
    echo -e "Running: ${YELLOW}$1${NC}"
    
    # Check file extension and run accordingly
    if [[ "$1" == *.py ]]; then
        python "$1"
    elif [[ "$1" == *.sh ]]; then
        bash "$1"
    elif [[ "$1" == *.js ]]; then
        node "$1"
    else
        echo -e "${RED}Unknown file type: $1${NC}"
        return 1
    fi
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Test passed: $1${NC}"
        return 0
    else
        echo -e "${RED}✗ Test failed: $1${NC}"
        return 1
    fi
}

function run_tests_in_dir() {
    local dir=$1
    local count=0
    local passed=0
    
    echo -e "\n${YELLOW}Running tests in: $dir${NC}"
    echo "------------------------"
    
    # Run all test files in the directory
    for test_file in "$dir"/*; do
        if [[ -f "$test_file" && "$test_file" == *test_* ]]; then
            ((count++))
            run_test_file "$test_file" && ((passed++))
            echo ""
        fi
    done
    
    echo -e "${YELLOW}Results for $dir:${NC} $passed/$count tests passed"
    return $((count - passed))
}

# Show usage if needed
function show_usage() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --all            Run all tests"
    echo "  --api            Run API tests only"
    echo "  --vulnerability  Run vulnerability tests only"
    echo "  --attack-path    Run attack path tests only"
    echo "  --risk           Run risk framework tests only"
    echo "  --integration    Run integration tests only"
    echo "  --help           Show this help message"
    echo ""
    echo "Example: $0 --api --vulnerability"
}

# No arguments - show usage
if [ $# -eq 0 ]; then
    show_usage
    exit 1
fi

# Process arguments
run_all=false
run_api=false
run_vulnerability=false
run_attack_path=false
run_risk=false
run_integration=false
failures=0

for arg in "$@"; do
    case $arg in
        --all)
            run_all=true
            ;;
        --api)
            run_api=true
            ;;
        --vulnerability)
            run_vulnerability=true
            ;;
        --attack-path)
            run_attack_path=true
            ;;
        --risk)
            run_risk=true
            ;;
        --integration)
            run_integration=true
            ;;
        --help)
            show_usage
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $arg${NC}"
            show_usage
            exit 1
            ;;
    esac
done

# Run tests based on arguments
if [ "$run_all" = true ]; then
    run_api=true
    run_vulnerability=true
    run_attack_path=true
    run_risk=true
    run_integration=true
fi

# Run tests for each selected category
if [ "$run_api" = true ]; then
    run_tests_in_dir "$SCRIPT_DIR/api"
    failures=$((failures + $?))
fi

if [ "$run_vulnerability" = true ]; then
    run_tests_in_dir "$SCRIPT_DIR/vulnerability"
    failures=$((failures + $?))
fi

if [ "$run_attack_path" = true ]; then
    run_tests_in_dir "$SCRIPT_DIR/attack_path"
    failures=$((failures + $?))
fi

if [ "$run_risk" = true ]; then
    run_tests_in_dir "$SCRIPT_DIR/risk"
    failures=$((failures + $?))
fi

if [ "$run_integration" = true ]; then
    run_tests_in_dir "$SCRIPT_DIR/integration"
    failures=$((failures + $?))
fi

# Summary
echo ""
echo "======================="
if [ $failures -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}$failures test(s) failed!${NC}"
    exit 1
fi
