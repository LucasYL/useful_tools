#!/bin/bash

# 测试视频ID
VIDEO_ID="dQw4w9WgXcQ"
SUMMARY_TYPE="short"
LANGUAGE="en"

# API端点
API_URL="http://localhost:8000/api/summarize"

# 显示要发送的请求
echo "测试发送请求到: $API_URL"
echo "请求体: {\"video_id\": \"$VIDEO_ID\", \"summary_type\": \"$SUMMARY_TYPE\", \"language\": \"$LANGUAGE\"}"

# 发送请求
curl -X POST $API_URL \
  -H "Content-Type: application/json" \
  -d "{\"video_id\": \"$VIDEO_ID\", \"summary_type\": \"$SUMMARY_TYPE\", \"language\": \"$LANGUAGE\"}" \
  -v

echo ""
echo "请求已发送，检查上述响应" 