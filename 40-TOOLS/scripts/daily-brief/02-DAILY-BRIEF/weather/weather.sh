#!/bin/bash
# Optimized Weather CLI for OpenClaw
# 优化的天气命令行工具

set -e

# 配置
CACHE_DIR="${TMPDIR:-/tmp}/weather-cache"
CACHE_TTL=${WEATHER_CACHE_TTL:-1800}  # 30 分钟
DEFAULT_LANG=${WEATHER_LANG:-zh}
DEFAULT_UNIT=${WEATHER_UNIT:-m}  # m=metric, u=imperial

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color

# 确保缓存目录存在
mkdir -p "$CACHE_DIR" 2>/dev/null || true

# 打印用法
usage() {
    cat << EOF
🌤️  天气查询工具 - 优化版

用法：$0 [选项] <地点>

选项:
  -f, --forecast     3 天预报
  -w, --week         周预报
  -c, --celsius      摄氏度 (默认)
  -u, --fahrenheit   华氏度
  -l, --lang <lang>  语言 (zh/en/ja/ko 等)
  -n, --no-cache     禁用缓存
  -h, --help         显示帮助

示例:
  $0 Beijing              # 北京实时天气
  $0 -f Shanghai          # 上海 3 天预报
  $0 -w "New York" -u     # 纽约周预报 (华氏度)
  $0 -l en London         # 伦敦天气 (英文)

EOF
    exit 0
}

# 获取缓存
get_cache() {
    local key="$1"
    local cache_file="$CACHE_DIR/$key"
    
    if [[ -f "$cache_file" ]]; then
        local cache_time=$(stat -f%m "$cache_file" 2>/dev/null || stat -c%Y "$cache_file" 2>/dev/null || echo 0)
        local now=$(date +%s)
        local age=$((now - cache_time))
        
        if [[ $age -lt $CACHE_TTL ]]; then
            echo -e "${GRAY}📦 从缓存读取 (剩余：$((CACHE_TTL - age))s)${NC}" >&2
            cat "$cache_file"
            return 0
        fi
    fi
    return 1
}

# 保存缓存
save_cache() {
    local key="$1"
    local data="$2"
    local cache_file="$CACHE_DIR/$key"
    echo "$data" > "$cache_file"
}

# 自动检测位置
detect_location() {
    echo -e "${CYAN}🔍 正在检测位置...${NC}" >&2
    
    # 尝试通过 IP 检测
    local city=$(curl -s --max-time 5 "https://ipapi.co/json/" 2>/dev/null | \
                 grep -o '"city":"[^"]*"' | cut -d'"' -f4 | head -1)
    
    if [[ -n "$city" ]]; then
        echo -e "${GREEN}📍 检测到：$city${NC}" >&2
        echo "$city"
        return 0
    fi
    
    # 备用方案
    echo -e "${YELLOW}⚠️  无法检测位置，使用默认：Beijing${NC}" >&2
    echo "Beijing"
}

# 获取天气
get_weather() {
    local location="$1"
    local format="$2"
    local lang="$3"
    local unit="$4"
    local no_cache="$5"
    
    # 构建 URL
    local encoded_location=$(echo "$location" | sed 's/ /+/g')
    local base_url="https://wttr.in/${encoded_location}"
    local params=()
    
    case "$format" in
        current) params+=("format=j1") ;;
        forecast) params+=("format=j1") ;;
        week) params+=("format=v2") ;;
        *) params+=("format=%l:+%c+%t+(feels+like+%f),+%w+wind,+%h+humidity") ;;
    esac
    
    [[ -n "$unit" ]] && params+=("$unit")
    [[ -n "$lang" ]] && params+=("lang=$lang")
    
    local url="$base_url"
    if [[ ${#params[@]} -gt 0 ]]; then
        url+="?$(IFS='&'; echo "${params[*]}")"
    fi
    
    # 缓存键
    local cache_key="weather_$(echo "$location$format$lang$unit" | md5sum | cut -d' ' -f1).txt"
    
    # 检查缓存
    if [[ "$no_cache" != "true" ]]; then
        local cached=$(get_cache "$cache_key")
        if [[ -n "$cached" ]]; then
            echo "$cached"
            return 0
        fi
    fi
    
    # 发送请求（带重试）
    local max_retries=3
    local retry=0
    while [[ $retry -lt $max_retries ]]; do
        echo -e "${CYAN}🌤️  正在获取天气数据...${NC}" >&2
        
        local response=$(curl -s --max-time 10 "$url" 2>/dev/null)
        
        if [[ -n "$response" ]]; then
            save_cache "$cache_key" "$response"
            echo "$response"
            return 0
        fi
        
        retry=$((retry + 1))
        if [[ $retry -lt $max_retries ]]; then
            sleep $((2 * retry))
        fi
    done
    
    echo -e "${RED}❌ 天气服务不可用（重试 $retry 次后失败）${NC}" >&2
    return 1
}

# 格式化输出（文本模式）
format_output_text() {
    local data="$1"
    local format="$2"
    
    if [[ "$format" == "current" ]]; then
        # 使用 wttr.in 的文本格式
        echo "$data"
    else
        echo "$data"
    fi
}

# 主程序
main() {
    local format="current"
    local lang="$DEFAULT_LANG"
    local unit="$DEFAULT_UNIT"
    local no_cache="false"
    local location=""
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -f|--forecast)
                format="forecast"
                shift
                ;;
            -w|--week)
                format="week"
                shift
                ;;
            -c|--celsius)
                unit="m"
                shift
                ;;
            -u|--fahrenheit)
                unit="u"
                shift
                ;;
            -l|--lang)
                lang="$2"
                shift 2
                ;;
            -n|--no-cache)
                no_cache="true"
                shift
                ;;
            -h|--help)
                usage
                ;;
            -*)
                echo -e "${RED}❌ 未知选项：$1${NC}" >&2
                usage
                ;;
            *)
                location="$1"
                shift
                ;;
        esac
    done
    
    # 如果没有指定位置，自动检测
    if [[ -z "$location" ]]; then
        location=$(detect_location)
    fi
    
    # 获取天气
    local weather_data
    if weather_data=$(get_weather "$location" "$format" "$lang" "$unit" "$no_cache"); then
        format_output_text "$weather_data" "$format"
    else
        exit 1
    fi
}

main "$@"
