# YouTube Summary Backend Tests

这个目录包含YouTube Summary应用的各种测试脚本。

## 测试脚本

### 数据库测试

- **test_db.py**: 测试数据库连接和表结构，整合了SQLAlchemy和Psycopg2的测试

### API测试

- **test_user_api.py**: 测试用户相关API，包括注册、登录和获取用户信息
- **test_youtube_api.py**: 测试YouTube元数据和文本转录API，包括提取视频ID、获取元数据和生成增强文本

### YouTube功能测试 

- **test_video.py**: 测试YouTube视频元数据提取功能
- **test_transcript.py**: 测试YouTube视频文本转录提取功能

## 使用方法

### 数据库测试

```bash
python -m tests.test_db
```

### 用户API测试

```bash
# 随机生成测试用户
python -m tests.test_user_api

# 测试已存在的用户
python -m tests.test_user_api --username testuser --password password
```

### YouTube API测试

```bash
# 使用默认测试视频
python -m tests.test_youtube_api

# 指定YouTube视频
python -m tests.test_youtube_api "https://www.youtube.com/watch?v=VIDEO_ID"

# 不保存输出
python -m tests.test_youtube_api --no-save
```

### 视频和文本转录测试

```bash
# 测试视频元数据
python -m tests.test_video

# 测试文本转录
python -m tests.test_transcript 

# 启用调试模式
python -m tests.test_transcript --debug
```

## 输出

测试结果会显示在控制台，部分测试还会将结果保存到`tests/output/VIDEO_ID/`目录中，包括：

- metadata.json: 视频元数据
- transcript.json: 视频文本转录
- enhanced_text.txt: 生成的增强文本 