# Word2048 Enhanced - 项目进度概览

> 📅 最后更新：2025-02-11
> 📦 仓库：[github.com/DahaiSun/2048](https://github.com/DahaiSun/2048)
> 🏷️ 当前版本：v2.5 (Multi-Wordbook)

---

## 📋 项目简介

Word2048 是一款基于经典 2048 玩法的英语单词学习游戏。内置 **23 本词书、8,385 个单词**，涵盖 Oxford 5000 核心词汇、12 个生活场景、8 个专题趣味词书及 CET-4/6 考试词汇，支持多词书自由切换、CEFR 分级选择，配有真人发音和中文翻译。

### 多平台支持

| 平台 | 技术栈 | 状态 |
|------|--------|------|
| 🌐 Web (PWA) | HTML5 / CSS3 / JavaScript | ✅ 已完成 |
| 📱 Android | Kotlin + Jetpack Compose + WebView | ✅ 已完成 |
| 🖥️ Desktop | Python + pywebview | ✅ 已完成 |

---

## 🎮 核心功能

| 功能 | 描述 | 状态 |
|------|------|------|
| 2048 游戏核心 | 4×4 网格，经典合并玩法 | ✅ |
| 词汇系统 | 23 本词书，8,385 个单词 | ✅ |
| 多词书切换 | 4 大分类：综合/场景/专题/考试，自由选择 | ✅ |
| CEFR 分级 | A1 / A2 / B1 / B2 / C1 多级选择 | ✅ |
| 中文翻译 | 100% 单词覆盖翻译 | ✅ |
| 单词发音 | WAV 音频 + 浏览器 TTS 兜底 | ✅ (95.2%) |
| 背景音乐 | BGM 播放与音量控制 | ✅ |
| 朗读音量 | 独立的单词发音音量控制 | ✅ |
| 音效反馈 | 合并/移动/胜利/结束 Web Audio 音效 | ✅ |
| 触控支持 | 全屏触控滑动（移动端） | ✅ |
| 鼠标支持 | 鼠标拖拽滑动（桌面端） | ✅ |
| 键盘支持 | 方向键 / WASD | ✅ |
| 离线使用 | Service Worker 缓存 (PWA) | ✅ |
| 数据持久化 | LocalStorage 保存进度/设置 | ✅ |
| 游戏统计 | 局数/最高分/学习单词数/游戏时间 | ✅ |
| 长单词自适应 | 方块内文字自动换行 | ✅ |

---

## 📊 词汇数据

### CEFR 等级分布

| 等级 | 单词数 | 有音频 | 有翻译 | 音频覆盖率 |
|------|--------|--------|--------|------------|
| A1 | 890 | 882 | 890 | 99.1% |
| A2 | 789 | 782 | 789 | 99.1% |
| B1 | 688 | 680 | 688 | 98.8% |
| B2 | 1,289 | 1,277 | 1,289 | 99.1% |
| C1 | 1,273 | 1,073 | 1,273 | 84.3% |
| **合计** | **4,929** | **4,694** | **4,929** | **95.2%** |

### 数据流水线

```
Oxford 5000 PDF
    ↓ (提取 + 翻译)
oxford_5000_merged_total_translated.csv (原始数据)
    ↓ (clean_vocabulary.py 清洗)
oxford_5000_cleaned.csv (清洗后 4,929 词)
    ↓ (生成 JS)
oxford_vocabulary.js (供游戏使用)
```

### 音频系统

```
Google Cloud TTS API
    ↓ (generate_tts.py 批量生成)
words/tts_delivery/audio/*.wav (4,803 个文件，337 MB)
    ↓ (vocabulary.js AudioPlayer 播放)
浏览器 Web Audio API  →  若无文件则 SpeechSynthesis TTS 兜底
```

---

## 📁 项目结构

```
word2048-enhanced/
├── index.html              # 主页面 (PWA 入口)
├── game.js                 # 游戏核心逻辑 (WordGame 类)
├── vocabulary.js           # 音频播放 + 词汇管理
├── wordbook-registry.js    # 词书注册系统
├── oxford_vocabulary.js    # Oxford 5000 词汇数据 (4,929 词)
├── styles.css              # 样式与动画
├── sw.js                   # Service Worker (离线缓存)
├── manifest.json           # PWA 配置
├── bgm.mp3                 # 背景音乐
├── icon.png                # 应用图标
├── app.py                  # Python 桌面封装 (pywebview)
├── README.md               # 项目文档
│
├── wordbooks/              # 扩展词书数据
│   ├── scene_food.js       # 🍔 食物饮料
│   ├── scene_clothing.js   # 👕 服饰穿着
│   ├── scene_home.js       # 🏠 家居房屋
│   ├── scene_transport.js  # 🚗 交通出行
│   ├── scene_health.js     # 🏥 健康身体
│   ├── scene_shopping.js   # 🛒 购物消费
│   ├── scene_nature.js     # 🌤️ 天气自然
│   ├── scene_entertainment.js # 🎭 娱乐爱好
│   ├── scene_travel.js     # ✈️ 旅行酒店
│   ├── scene_work.js       # 💼 工作职场
│   ├── scene_school.js     # 🏫 学校教育
│   ├── scene_social.js     # 💬 社交情感
│   ├── topic_tech.js       # 💻 科技互联网
│   ├── topic_social_media.js # 📱 社交媒体
│   ├── topic_gaming.js     # 🎮 游戏电竞
│   ├── topic_finance.js    # 💰 商务金融
│   ├── topic_marketing.js  # 📊 营销广告
│   ├── topic_film.js       # 🎬 电影影视
│   ├── topic_medical.js    # 🏥 医学用语
│   ├── topic_science.js    # 🔬 科学实验
│   ├── cet4_vocabulary.js  # 🎓 CET-4 四级
│   └── cet6_vocabulary.js  # 🎓 CET-6 六级
│
├── words/                  # 词汇数据与工具
│   ├── oxford_5000_cleaned.csv       # 清洗后的词汇表
│   ├── missing_audio.txt             # 缺失音频清单 (235 词)
│   ├── clean_vocabulary.py           # CSV 清洗 + JS 生成脚本
│   ├── generate_scene_wordbooks.py   # 场景词书生成脚本
│   ├── generate_cet_wordbooks.py     # CET-4/6 词书生成脚本
│   ├── generate_topic_wordbooks.py   # 专题词书生成脚本
│   ├── generate_tts.py               # TTS 音频生成脚本
│   ├── requirements.txt              # Python 依赖
│   └── tts_delivery/
│       ├── words_manifest.json       # 音频索引
│       └── audio/                    # WAV 音频文件 (4,803 个)
│
└── android/                # Android 原生应用
    ├── build.gradle.kts
    ├── gradlew
    └── app/src/main/
        ├── AndroidManifest.xml
        └── java/com/example/word2048/
            ├── MainActivity.kt       # WebView 封装
            └── SplashScreen.kt       # 启动屏
```

---

## 🔄 版本历史

| Commit | 描述 | 日期 |
|--------|------|------|
| `8741f6c` | 新增 8 个专题词书（科技/社媒/游戏/金融/营销/影视/医学/科学） | 最新 |
| `f6059f4` | 多词书系统：词书注册中心 + 12 场景词书 + CET-4/6 考试词书 | |
| `08dfa8a` | 新增项目进度文档 (PROJECT_PROGRESS.md) | |
| `d627dfe` | 重命名 9 个音频 + 删除 32 个垃圾/合并文件 | |
| `b95126b` | 修复损坏的音频文件名并更新词汇 JS | |
| `7cc4b12` | 清洗 Oxford 5000 词汇数据 (修复 472 条异常) | |
| `190c1b9` | 合并 Android 项目到统一仓库 | |
| `bad0fe2` | 长单词方块内自动换行 (v2.4) | |
| `dc75c65` | 优化移动端触控（passive events、降低阈值） | |
| `e8c9f4b` | 清理 Android 构建产物 | |
| `23b1eac` | 修复点击事件，CSS 防选中替代 preventDefault | |
| `159c4d9` | 鼠标控制增强 + 版本号 v2.1 | |
| `0df202a` | 添加鼠标滑动支持（桌面端） | |
| `88e8d0f` | 扩展触控区域至全屏 | |
| `990652b` | 部署：Service Worker v3 全量更新 | |

---

## ⚠️ 待办事项

### 🔴 高优先级

- [ ] **补充 235 个缺失音频**
  清单见 `words/missing_audio.txt`，按 CEFR 等级分布：
  - A1: 8 词 (bathroom, cannot, dad, front, ice, machine, Saturday, statement)
  - A2: 5 词 (anybody, brilliant, education, immediately, opportunity, safe, towel)
  - B1: 6 词 (bite, dust, fixed, immediate, perfectly, queue, sensible, various)
  - B2: 12 词 (angle, beneficial, chief, conservation, distinct, hearing, hip, litter, overcome, shadow, spill, therapy)
  - C1: ~204 词 (占缺失总量 87%)

  > 解决方案：使用 `generate_tts.py` 配合 Google Cloud TTS API 批量生成

### 🟡 中优先级

- [ ] **清理剩余 96 个带词性标注的音频文件名**
  如 `bath n.bathroom.wav`、`cut v.dad.wav` 等，音频内容可能只对应文件名中的第一个单词
- [ ] **处理 11 个编号变体音频**
  如 `close 2.wav`、`live2.wav` 等，需确认是否为同一单词的不同义项发音

### 🟢 低优先级

- [ ] Android 应用发布到 Google Play
- [ ] 添加单词收藏/复习功能
- [ ] 添加学习进度报告

---

## 📚 词书扩展路线图

### 架构：多词书注册系统

```
wordbook-registry.js          词书注册中心
     ↑ registerWordbook()
     ├── oxford_vocabulary.js   📖 Oxford 5000 (A1-C1)
     ├── wordbooks/scene_*.js   🎯 12 个场景词书
     ├── wordbooks/topic_*.js   🧩 8 个专题词书
     ├── wordbooks/cet4_*.js    🎓 四级词汇
     ├── wordbooks/cet6_*.js    🎓 六级词汇
     └── (未来可扩展更多)
           ↓
     vocabulary.js → VocabularyManager (多词书切换)
           ↓
     game.js → 词书选择UI + 等级选择UI
```

### 词书清单

| 批次 | 词书 | 词数 | 分级方式 | 状态 |
|------|------|------|----------|------|
| **第一批** | 📖 Oxford 5000 | 4,929 | CEFR A1-C1 | ✅ 完成 |
| **第一批** | 🍔 食物饮料 | 129 | 单级 | ✅ 完成 |
| **第一批** | 👕 服饰穿着 | 64 | 单级 | ✅ 完成 |
| **第一批** | 🏠 家居房屋 | 87 | 单级 | ✅ 完成 |
| **第一批** | 🚗 交通出行 | 85 | 单级 | ✅ 完成 |
| **第一批** | 🏥 健康身体 | 131 | 单级 | ✅ 完成 |
| **第一批** | 🛒 购物消费 | 83 | 单级 | ✅ 完成 |
| **第一批** | 🌤️ 天气自然 | 127 | 单级 | ✅ 完成 |
| **第一批** | 🎭 娱乐爱好 | 121 | 单级 | ✅ 完成 |
| **第一批** | ✈️ 旅行酒店 | 90 | 单级 | ✅ 完成 |
| **第一批** | 💼 工作职场 | 117 | 单级 | ✅ 完成 |
| **第一批** | 🏫 学校教育 | 106 | 单级 | ✅ 完成 |
| **第一批** | 💬 社交情感 | 132 | 单级 | ✅ 完成 |
| **第一批** | 🎓 CET-4 四级 | 542 | 高频/核心 | ✅ 完成 |
| **第一批** | 🎓 CET-6 六级 | 370 | 高频/核心 | ✅ 完成 |
| **第二批** | 💻 科技互联网 | 154 | 单级 | ✅ 完成 |
| **第二批** | 📱 社交媒体 | 117 | 单级 | ✅ 完成 |
| **第二批** | 🎮 游戏电竞 | 169 | 单级 | ✅ 完成 |
| **第二批** | 💰 商务金融 | 148 | 单级 | ✅ 完成 |
| **第二批** | 📊 营销广告 | 145 | 单级 | ✅ 完成 |
| **第二批** | 🎬 电影影视 | 170 | 单级 | ✅ 完成 |
| **第二批** | 🏥 医学用语 | 153 | 单级 | ✅ 完成 |
| **第二批** | 🔬 科学实验 | 216 | 单级 | ✅ 完成 |
| 第三批 | 🌍 雅思 IELTS | ~1,500 | 学术/生活 | 📋 计划中 |
| 第三批 | 📖 托福 TOEFL | ~1,500 | 学术核心 | 📋 计划中 |
| 第三批 | 🏫 中考词汇 | ~1,500 | 核心/拓展 | 📋 计划中 |
| 第三批 | 🏫 高考词汇 | ~2,000 | 核心/拓展 | 📋 计划中 |
| 第三批 | 🐾 动物世界 | ~150 | 单级 | 📋 计划中 |

---

## 🛠️ 开发指南

### 环境要求

```bash
# Web 开发 - 无需构建，直接打开 index.html
# 或使用任意 HTTP 服务器：
python -m http.server 8000

# 数据处理
pip install pandas google-cloud-texttospeech

# Android 构建
# 需要 Android Studio + SDK 34
```

### 常用脚本

```bash
# 清洗词汇数据并重新生成 oxford_vocabulary.js
python words/clean_vocabulary.py

# 生成场景词书 (12 本 → wordbooks/scene_*.js)
python words/generate_scene_wordbooks.py

# 生成专题词书 (8 本 → wordbooks/topic_*.js)
python words/generate_topic_wordbooks.py

# 生成 CET-4/6 考试词书 (2 本 → wordbooks/cet4/6_vocabulary.js)
python words/generate_cet_wordbooks.py

# 生成缺失的 TTS 音频
python words/generate_tts.py

# 验证所有词书加载
node -e "global.WORDBOOK_REGISTRY={};global.registerWordbook=function(i,c){WORDBOOK_REGISTRY[i]=c};require('./oxford_vocabulary.js');require('fs').readdirSync('./wordbooks').filter(f=>f.endsWith('.js')).forEach(f=>require('./wordbooks/'+f));console.log(Object.keys(WORDBOOK_REGISTRY).length,'wordbooks loaded')"
```

---

## 📈 项目统计

| 指标 | 数值 |
|------|------|
| 项目总大小 | ~550 MB |
| 核心代码 | ~77 KB (HTML+CSS+JS) |
| 词书数据 | ~600 KB (oxford_vocabulary.js + 22 个词书 JS) |
| 音频文件 | 337 MB (4,803 WAV) |
| 词书总数 | 23 本（1 综合 + 12 场景 + 8 专题 + 2 考试） |
| 词汇总量 | 8,385 词 |
| 翻译覆盖率 | 100% |
| 音频覆盖率 | Oxford 95.2% / 场景 ~85% / 专题 ~78% / CET ~68% |
| Git 提交数 | 15 |
| Android minSDK | 24 (Android 7.0+) |
