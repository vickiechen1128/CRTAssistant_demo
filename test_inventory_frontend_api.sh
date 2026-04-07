#!/bin/bash
#
# 台账管理前端 API 测试脚本
# 测试所有新增的前端功能对应的接口
#

set -e

BASE_URL="http://localhost:8000/api/v1/inventory"
APP_ID="1a57415c-c9f8-4368-9d03-54fa32126baa"

echo "=========================================="
echo "  台账管理前端 API 测试"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# 测试计数
TOTAL=0
PASSED=0
FAILED=0

# 测试函数
test_api() {
    local name=$1
    local url=$2
    local method=${3:-GET}
    local data=${4:-}
    
    TOTAL=$((TOTAL + 1))
    
    echo -n "测试 $name ... "
    
    if [ "$method" = "POST" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST "$url" \
            -H "Content-Type: application/json" \
            -d "$data" 2>/dev/null)
    elif [ "$method" = "PUT" ]; then
        response=$(curl -s -w "\n%{http_code}" -X PUT "$url" \
            -H "Content-Type: application/json" \
            -d "$data" 2>/dev/null)
    elif [ "$method" = "DELETE" ]; then
        response=$(curl -s -w "\n%{http_code}" -X DELETE "$url" 2>/dev/null)
    else
        response=$(curl -s -w "\n%{http_code}" "$url" 2>/dev/null)
    fi
    
    http_code=$(echo "$response" | tail -n1)
    
    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        echo -e "${GREEN}✓ 通过${NC} (HTTP $http_code)"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${RED}✗ 失败${NC} (HTTP $http_code)"
        echo "  响应: $(echo "$response" | head -n1 | cut -c1-100)"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

echo "【基础接口测试】"
echo "------------------------------"
test_api "获取台账汇总" "$BASE_URL/summary"
test_api "获取应用列表" "$BASE_URL/applications"
test_api "获取应用详情" "$BASE_URL/applications/$APP_ID"

echo ""
echo "【功能模块接口测试】"
echo "------------------------------"
test_api "获取功能模块列表" "$BASE_URL/applications/$APP_ID/modules"
test_api "获取功能模块树" "$BASE_URL/applications/$APP_ID/modules/tree"

# 创建功能模块测试
echo -n "测试 创建功能模块 ... "
MODULE_RESPONSE=$(curl -s -X POST "$BASE_URL/applications/$APP_ID/modules" \
    -H "Content-Type: application/json" \
    -d '{"module_code":"test_module_'$(date +%s)'","module_name":"测试模块","version":"1.0.0","description":"测试功能模块"}' 2>/dev/null)

if echo "$MODULE_RESPONSE" | grep -q "id"; then
    MODULE_ID=$(echo "$MODULE_RESPONSE" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
    echo -e "${GREEN}✓ 通过${NC} (模块ID: $MODULE_ID)"
    PASSED=$((PASSED + 1))
    TOTAL=$((TOTAL + 1))
    
    # 继续测试其他模块接口
    test_api "获取功能模块详情" "$BASE_URL/applications/$APP_ID/modules/$MODULE_ID"
    test_api "更新功能模块" "$BASE_URL/applications/$APP_ID/modules/$MODULE_ID" PUT '{"module_name":"更新后的模块名","description":"更新描述"}'
else
    echo -e "${RED}✗ 失败${NC}"
    echo "  响应: $MODULE_RESPONSE"
    FAILED=$((FAILED + 1))
    TOTAL=$((TOTAL + 1))
fi

echo ""
echo "【生命周期日志接口测试】"
echo "------------------------------"
test_api "获取生命周期日志列表" "$BASE_URL/applications/$APP_ID/logs"
test_api "获取时间线" "$BASE_URL/applications/$APP_ID/timeline"
test_api "获取日志类型" "$BASE_URL/applications/$APP_ID/logs/types"
test_api "获取日志统计" "$BASE_URL/applications/$APP_ID/logs/statistics"

# 创建日志测试
echo -n "测试 创建生命周期日志 ... "
LOG_RESPONSE=$(curl -s -X POST "$BASE_URL/applications/$APP_ID/logs" \
    -H "Content-Type: application/json" \
    -d '{"log_type":"manual","event_title":"测试事件","description":"测试生命周期日志","operator":"test_user"}' 2>/dev/null)

if echo "$LOG_RESPONSE" | grep -q "id"; then
    LOG_ID=$(echo "$LOG_RESPONSE" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
    echo -e "${GREEN}✓ 通过${NC} (日志ID: $LOG_ID)"
    PASSED=$((PASSED + 1))
    TOTAL=$((TOTAL + 1))
    
    test_api "获取日志详情" "$BASE_URL/applications/$APP_ID/logs/$LOG_ID"
else
    echo -e "${RED}✗ 失败${NC}"
    echo "  响应: $LOG_RESPONSE"
    FAILED=$((FAILED + 1))
    TOTAL=$((TOTAL + 1))
fi

echo ""
echo "=========================================="
echo "  测试结果汇总"
echo "=========================================="
echo -e "总测试数: $TOTAL"
echo -e "${GREEN}通过: $PASSED${NC}"
echo -e "${RED}失败: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}所有测试通过！✓${NC}"
    exit 0
else
    echo -e "${RED}存在失败的测试，请检查。${NC}"
    exit 1
fi
