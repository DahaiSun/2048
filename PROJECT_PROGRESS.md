# Word2048 Enhanced - 项目进度概览

> 📅 最后更新：2025-06
> 📦 仓库：[github.com/DahaiSun/2048](https://github.com/DahaiSun/2048)
> 🏷️ 当前版本：v2.4 (Word Wrap)

---

## 📋 项目简介

Word2048 是一款基于经典 2048 玩法的英语单词学习游戏。玩家在合并方块的过程中学习牛津 5000 核心词汇（Oxford 5000），支持 CEFR A1-C1 五个难度等级，配有真人发音和中文翻译。

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
| 词汇系统 | Oxford 5000 词汇，4929 个单词 | ✅ |
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
├── oxford_vocabulary.js    # 生成的词汇数据 (4,929 词)
├── styles.css              # 样式与动画
├── sw.js                   # Service Worker (离线缓存)
├── manifest.json           # PWA 配置
├── bgm.mp3                 # 背景音乐
├── icon.png                # 应用图标
├── app.py                  # Python 桌面封装 (pywebview)
├── README.md               # 项目文档
│
├── words/                  # 词汇数据与工具
│   ├── oxford_5000_cleaned.csv       # 清洗后的词汇表
│   ├── missing_audio.txt             # 缺失音频清单 (235 词)
│   ├── clean_vocabulary.py           # CSV 清洗 + JS 生成脚本
│   ├── fix_audio_filenames.py        # 音频文件名修复 (Step 1)
│   ├── fix_audio_step2.py            # 音频清理 (Step 2)
│   ├── generate_tts.py               # TTS 音频生成脚本
│   ├── generate_vocabulary_js.py     # JS 生成脚本
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
| `d627dfe` | 重命名 9 个音频 + 删除 32 个垃圾/合并文件 | 最新 |
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
- [ ] 添加更多词汇集（如雅思/托福高频词）
- [ ] 添加单词收藏/复习功能
- [ ] 添加学习进度报告

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
# 清洗词汇数据并重新生成 JS
python words/clean_vocabulary.py

# 生成缺失的 TTS 音频
python words/generate_tts.py

# 修复音频文件名
python words/fix_audio_step2.py
```

---

## 📈 项目统计

| 指标 | 数值 |
|------|------|
| 项目总大小 | 546 MB |
| 代码文件 | ~55 KB (HTML+CSS+JS) |
| 音频文件 | 337 MB (4,803 WAV) |
| 词汇总量 | 4,929 词 |
| 翻译覆盖率 | 100% |
| 音频覆盖率 | 95.2% |
| Git 提交数 | 12 |
| Android minSDK | 24 (Android 7.0+) |
