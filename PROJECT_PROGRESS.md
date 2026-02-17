# Word2048 Enhanced - 项目进度概览

> 📅 最后更新：2026-02-17
> 📦 仓库：[github.com/DahaiSun/2048](https://github.com/DahaiSun/2048)
> 🏷️ 当前版本：v2.8 (Classic 2048 UI + 5 Oxford + 19 Scene + 17 Topic + 2 Exam)

---

## 📋 项目简介

Word2048 是一款基于经典 2048 玩法的英语单词学习游戏。内置 **43 本词书、覆盖 5,999 个唯一单词**（各词书合计 10,563 词次），涵盖 Oxford 5000 核心词汇（按 CEFR 拆分为 5 本独立词书）、19 个生活场景、17 个专题趣味词书及 CET-4/6 考试词汇，支持多词书自由切换，配有真人发音和中文翻译。UI 采用经典 2048 暖色调风格。

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
| 词汇系统 | 43 本词书，5,999 个唯一单词 | ✅ |
| 多词书切换 | 5 大分类：Oxford/场景/专题/考试/综合，双列布局 | ✅ |
| 词书独立配色 | 每本词书独立 HSL 色相，卡片/方块跟随主题色 | ✅ |
| 经典 2048 配色 | 方块使用原版 2048 经典纯色（无渐变） | ✅ |
| 单词去重队列 | 每轮优先出现未见过的单词，全部出完再循环 | ✅ |
| 语境化翻译 | 100% 覆盖，多义词按词书领域匹配专业释义 | ✅ |
| 单词发音 | WAV 音频 + 浏览器 TTS 兜底 | ✅ (100%) |
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
| A1 | 890 | 890 | 890 | 100% |
| A2 | 789 | 789 | 789 | 100% |
| B1 | 688 | 688 | 688 | 100% |
| B2 | 1,289 | 1,289 | 1,289 | 100% |
| C1 | 1,273 | 1,273 | 1,273 | 100% |
| **合计** | **4,929** | **4,929** | **4,929** | **100%** |

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
Google Cloud TTS API (Chirp 3 HD - Zephyr)
    ↓ (generate_tts.py / generate_missing_audio.py 批量生成)
words/tts_delivery/audio/*.wav (5,644 个文件，393 MB)
    ↓ (vocabulary.js AudioPlayer 播放)
浏览器 Web Audio API  →  若无文件则 SpeechSynthesis TTS 兜底
```

### 多义词语境化翻译问题

**问题**：英语中大量多义词在不同领域有完全不同的含义，但词书生成时统一使用了通用词典释义，导致翻译与词书场景不匹配。例如：

| 单词 | 通用释义（错误） | 金融词书 | 体育词书 | 音乐词书 |
|------|------------------|----------|----------|----------|
| pitch | 沥青 | — | 球场 | 音高 |
| score | 分数 | — | — | 乐谱; 总谱 |
| bond | 纽带 | 债券 | — | — |
| stock | 库存 | 股票 | — | — |
| return | 返回 | 回报; 收益率 | — | — |
| key | 钥匙 | — | — | 调; 琴键 |
| track | 追踪 | — | 跑道; 赛道 | 曲目; 音轨 |
| court | 法庭 | — | 球场 | — |
| board | 木板 | — | 滑板 | — |

**影响范围**：38 本词书（17 专题 + 19 场景 + 2 CET）中累计 1,388 个词条存在翻译问题。

**解决方案**：分四轮修正——

1. **第一轮（手动精修 25 词）**：扫描全部 1,341 个跨词书重复词，修正 25 个翻译不一致的多义词（如 bore、athletics、bankrupt 等措辞统一，counsel、liability 等语境修正）
2. **第二轮（脚本批量修正 607 词）**：逐词书审查全部词条翻译，编写 `fix_translations.js` 自动化替换脚本，按词书领域逐一修正。涵盖 17 本专题词书（452 处）和 19 本场景词书（155 处）
3. **第三轮（全面重扫修正 707 词）**：7 组并行扫描代理重新检查所有 38 个词书文件，发现并修正剩余的领域翻译不匹配、乱码字符（如 使氮丧→使沮丧、降石坑→陨石坑、俆虏→俘虏、呕吟→呻吟、灌溢→灌溉）、截断翻译（如 控→控告、委→任命）及完全错误的翻译（如 broil 炒→炙烤）
4. **第四轮（CET 收尾修正 49 词）**：最终复检发现 CET-4/6 词书仍存在形容词缺少"的"字、翻译过于简略等问题，逐一修正后全部 38 个词书通过复检

| 轮次 | 修正数 | Commit | 说明 |
|------|--------|--------|------|
| 第一轮 | 25 | `7d1662f` | 手动修正跨词书不一致 |
| 第二轮 | 607 | `32ebf94` | 首次批量语境化修正 |
| 第三轮 | 707 | `4dec5fd` | 全面重扫深度修正 |
| 第四轮 | 49 | `0f1497b` | CET 词书收尾修正 |
| **合计** | **1,388** | | **全部 38 个词书文件复检通过** |

**预防措施**：后续新增词书时，生成脚本应根据词书领域自动选取领域释义（而非通用词典首义）。

---

## 📁 项目结构

```
word2048-enhanced/
├── index.html              # 主页面 (PWA 入口)
├── game.js                 # 游戏核心逻辑 (WordGame 类)
├── vocabulary.js           # 音频播放 + 词汇管理
├── wordbook-registry.js    # 词书注册系统
├── oxford_vocabulary.js    # Oxford 5000 词汇数据 (4,929 词, 拆分注册为 5 本独立词书)
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
│   ├── scene_fitness.js    # 🏋️ 运动健身
│   ├── scene_music.js      # 🎵 音乐乐器
│   ├── scene_animals.js    # 🐾 宠物动物
│   ├── scene_plants.js     # 🌿 植物花卉
│   ├── scene_festivals.js  # 🎄 节日文化
│   ├── scene_cooking.js    # 🍳 烹饪厨房
│   ├── scene_law.js        # ⚖️ 法律法规
│   ├── topic_tech.js       # 💻 科技互联网
│   ├── topic_social_media.js # 📱 社交媒体
│   ├── topic_gaming.js     # 🎮 游戏电竞
│   ├── topic_finance.js    # 💰 商务金融
│   ├── topic_marketing.js  # 📊 营销广告
│   ├── topic_film.js       # 🎬 电影影视
│   ├── topic_medical.js    # 🏥 医学用语
│   ├── topic_science.js    # 🔬 科学实验
│   ├── topic_space.js      # 🚀 太空航天
│   ├── topic_art.js        # 🎨 艺术设计
│   ├── topic_politics.js   # 🏛️ 政治外交
│   ├── topic_math.js       # 📐 数学逻辑
│   ├── topic_environment.js # 🌍 环保生态
│   ├── topic_psychology.js # 🧠 心理学
│   ├── topic_sports.js     # ⚽ 体育赛事
│   ├── topic_architecture.js # 🏗️ 建筑工程
│   ├── topic_ai.js         # 🤖 人工智能
│   ├── cet4_vocabulary.js  # 🎓 CET-4 四级
│   └── cet6_vocabulary.js  # 🎓 CET-6 六级
│
├── words/                  # 词汇数据与工具
│   ├── oxford_5000_cleaned.csv       # 清洗后的词汇表
│   ├── missing_audio.txt             # 原始缺失音频清单 (已补全)
│   ├── all_missing_audio.txt         # 全词书缺失音频清单 (已补全)
│   ├── generate_missing_audio.py     # 缺失音频批量生成脚本
│   ├── clean_vocabulary.py           # CSV 清洗 + JS 生成脚本
│   ├── generate_scene_wordbooks.py   # 场景词书生成脚本
│   ├── generate_cet_wordbooks.py     # CET-4/6 词书生成脚本
│   ├── generate_topic_wordbooks.py   # 专题词书生成脚本
│   ├── generate_tts.py               # TTS 音频生成脚本
│   ├── requirements.txt              # Python 依赖
│   └── tts_delivery/
│       ├── words_manifest.json       # 音频索引
│       └── audio/                    # WAV 音频文件 (5,644 个)
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
| `0f1497b` | 第四轮修正 CET4/CET6 词书 49 个翻译问题，全部 38 本词书复检通过 | 2026-02-17 |
| `4dec5fd` | 第三轮批量修正 707 个词书翻译，全面语境化所有词书 | 2026-02-17 |
| `32ebf94` | 批量修正 607 个词书翻译，确保语境化翻译准确 | 2026-02-15 |
| `7d1662f` | 修正 25 个跨词书翻译不一致的多义词 | 2026-02-15 |
| `8ff4a5b` | Oxford 5000 拆分为 5 本独立词书，新建 Oxford 分组 | 2026-02-15 |
| `0e02f2e` | UI 全面美化为经典 2048 暖色调风格 | 2026-02-15 |
| `38eed97` | 方块配色改为经典原版 2048 纯色 | 2026-02-15 |
| `a8853cf` | 词书选择器两列布局 + 每词书独立配色 + 单词去重队列 | 2026-02-15 |
| `6f8bc85` | 生成 465 个缺失音频，全部 39 本词书音频覆盖率 100% (v2.8) | 2026-02-14 |
| `42ebc53` | 生成 841 个缺失音频，23 本词书音频覆盖率 100% | 2026-02-12 |
| `3e585bf` | 更新 PROJECT_PROGRESS.md | |
| `8741f6c` | 新增 8 个专题词书（科技/社媒/游戏/金融/营销/影视/医学/科学） | |
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

### ✅ 已完成

- [x] **补充 841 个缺失音频** — 使用 `generate_missing_audio.py` + Google Cloud TTS Chirp 3 HD 批量生成，全部 23 本词书音频覆盖率达到 **100%**
- [x] **补充 465 个新词书缺失音频** — 第三批 9 个专题词书 + 第四批 7 个场景词书，使用 `generate_missing_audio.py` + Google Cloud TTS Chirp 3 HD 批量生成，全部 39 本词书音频覆盖率达到 **100%**（2026-02-14）
- [x] **修正 1,388 个多义词语境化翻译** — 四轮修正全面覆盖 38 本词书（17 专题 + 19 场景 + 2 CET），修正所有翻译与词书领域不匹配的词条、乱码字符、截断翻译，最终全部词书通过复检（2026-02-17，详见下方「多义词翻译问题」章节）

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
     ├── oxford_vocabulary.js   📖 Oxford 5000 → 拆分为 5 本独立词书 (A1/A2/B1/B2/C1)
     ├── wordbooks/scene_*.js   🎯 19 个场景词书
     ├── wordbooks/topic_*.js   🧩 17 个专题词书
     ├── wordbooks/cet4_*.js    🎓 四级词汇
     ├── wordbooks/cet6_*.js    🎓 六级词汇
     └── (未来可扩展更多)
           ↓
     vocabulary.js → VocabularyManager (多词书切换 + 单词去重队列)
           ↓
     game.js → 词书选择UI (双列布局 + 5 大分组 + 每词书独立配色)
```

### 词书清单

| 批次 | 词书 | 词数 | 分级方式 | 状态 |
|------|------|------|----------|------|
| **第一批** | 🌱 Oxford A1 入门 | 890 | 单级 | ✅ 完成 |
| **第一批** | 🌿 Oxford A2 初级 | 789 | 单级 | ✅ 完成 |
| **第一批** | 🌳 Oxford B1 中级 | 688 | 单级 | ✅ 完成 |
| **第一批** | 🔥 Oxford B2 中高级 | 1,289 | 单级 | ✅ 完成 |
| **第一批** | ⚡ Oxford C1 高级 | 1,273 | 单级 | ✅ 完成 |
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
| **第四批** | 🏋️ 运动健身 | 144 | 单级 | ✅ 完成 |
| **第四批** | 🎵 音乐乐器 | 124 | 单级 | ✅ 完成 |
| **第四批** | 🐾 宠物动物 | 138 | 单级 | ✅ 完成 |
| **第四批** | 🌿 植物花卉 | 117 | 单级 | ✅ 完成 |
| **第四批** | 🎄 节日文化 | 121 | 单级 | ✅ 完成 |
| **第四批** | 🍳 烹饪厨房 | 145 | 单级 | ✅ 完成 |
| **第四批** | ⚖️ 法律法规 | 145 | 单级 | ✅ 完成 |
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
| **第三批** | 🚀 太空航天 | 132 | 单级 | ✅ 完成 |
| **第三批** | 🎨 艺术设计 | 124 | 单级 | ✅ 完成 |
| **第三批** | 🏛️ 政治外交 | 127 | 单级 | ✅ 完成 |
| **第三批** | 📐 数学逻辑 | 135 | 单级 | ✅ 完成 |
| **第三批** | 🌍 环保生态 | 124 | 单级 | ✅ 完成 |
| **第三批** | 🧠 心理学 | 155 | 单级 | ✅ 完成 |
| **第三批** | ⚽ 体育赛事 | 130 | 单级 | ✅ 完成 |
| **第三批** | 🏗️ 建筑工程 | 156 | 单级 | ✅ 完成 |
| **第三批** | 🤖 人工智能 | 161 | 单级 | ✅ 完成 |
| 第五批 | 🌍 雅思 IELTS | ~1,500 | 学术/生活 | 📋 计划中 |
| 第五批 | 📖 托福 TOEFL | ~1,500 | 学术核心 | 📋 计划中 |
| 第五批 | 🏫 中考词汇 | ~1,500 | 核心/拓展 | 📋 计划中 |
| 第五批 | 🏫 高考词汇 | ~2,000 | 核心/拓展 | 📋 计划中 |

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

# 生成场景词书 (19 本 → wordbooks/scene_*.js)
python words/generate_scene_wordbooks.py

# 生成专题词书 (17 本 → wordbooks/topic_*.js)
python words/generate_topic_wordbooks.py

# 生成 CET-4/6 考试词书 (2 本 → wordbooks/cet4/6_vocabulary.js)
python words/generate_cet_wordbooks.py

# 生成全量 TTS 音频 (Oxford 5000)
python words/generate_tts.py

# 补充缺失音频 (扫描所有词书，只生成缺失的)
python words/generate_missing_audio.py

# 验证所有词书加载
node -e "global.WORDBOOK_REGISTRY={};global.registerWordbook=function(i,c){WORDBOOK_REGISTRY[i]=c};require('./oxford_vocabulary.js');require('fs').readdirSync('./wordbooks').filter(f=>f.endsWith('.js')).forEach(f=>require('./wordbooks/'+f));console.log(Object.keys(WORDBOOK_REGISTRY).length,'wordbooks loaded')"
```

---

## 🔊 音频生成指南 (Google Cloud TTS)

新增词书后，部分单词可能缺少 WAV 音频文件。使用以下流程补充：

### 前置条件

1. **Google Cloud 项目**：已启用 Text-to-Speech API，已开通计费
2. **认证**：运行 `gcloud auth application-default login`（或设置 `GOOGLE_APPLICATION_CREDENTIALS` 环境变量）
3. **Python 依赖**：`pip install pandas google-cloud-texttospeech`

### 步骤 1：扫描缺失音频

```bash
node -e "
global.WORDBOOK_REGISTRY={};
global.registerWordbook=function(i,c){WORDBOOK_REGISTRY[i]=c};
require('./oxford_vocabulary.js');
var fs=require('fs');
fs.readdirSync('./wordbooks').filter(f=>f.endsWith('.js')).forEach(f=>require('./wordbooks/'+f));
var audioDir='words/tts_delivery/audio';
var audioFiles=new Set(fs.readdirSync(audioDir).map(f=>f.replace('.wav','')));
var allMissing=new Set();
Object.keys(WORDBOOK_REGISTRY).forEach(id=>{
  var wb=WORDBOOK_REGISTRY[id];
  Object.keys(wb.levels).forEach(lv=>{
    wb.levels[lv].words.forEach(w=>{
      if(audioFiles.has(w.word)===false) allMissing.add(w.word);
    });
  });
});
console.log(Array.from(allMissing).sort().join('\n'));
" > words/all_missing_audio.txt
```

### 步骤 2：批量生成音频

```bash
# 先预览要生成的单词列表
python words/generate_missing_audio.py --dry-run

# 确认无误后执行生成
python words/generate_missing_audio.py
```

### 步骤 3：重新生成词书 JS（更新音频引用）

```bash
python words/generate_topic_wordbooks.py
python words/generate_scene_wordbooks.py
```

### TTS 配置

| 参数 | 值 |
|------|-----|
| API | Google Cloud Text-to-Speech |
| 声音模型 | `en-US-Chirp3-HD-Zephyr` |
| 语言 | `en-US` |
| 输出格式 | WAV (LINEAR16) |
| SSML 尾部填充 | `<break time="300ms"/>` 防止音频截断 |
| 项目 ID | 在 `generate_missing_audio.py` 中配置 `GOOGLE_CLOUD_PROJECT_ID` |
| 输出目录 | `words/tts_delivery/audio/` |

### 常见问题

- **Quota exceeded / API not enabled**：在 `client_options` 中显式传入 `quota_project_id`（脚本已内置）
- **音频截断**：使用 SSML `<break time="300ms"/>` 尾部填充（脚本已内置）
- **部分失败**：失败的单词会自动保存到 `words/tts_failed.txt`，可重新运行脚本补充

---

## 📈 项目统计

| 指标 | 数值 |
|------|------|
| 项目总大小 | ~600 MB |
| 核心代码 | ~77 KB (HTML+CSS+JS) |
| 词书数据 | ~1 MB (oxford_vocabulary.js + 38 个词书 JS) |
| 音频文件 | ~420 MB (6,107 WAV) |
| 词书总数 | 43 本（5 Oxford + 19 场景 + 17 专题 + 2 考试） |
| 唯一词汇量 | 5,999 词（各词书合计 10,563 词次） |
| 翻译覆盖率 | 100% |
| 音频覆盖率 | 100%（全部 43 本词书） |
| Git 提交数 | 22+ |
| Android minSDK | 24 (Android 7.0+) |
