// ============================================================
// Word2048 词汇系统 - Oxford 5000 + WAV音频
// ============================================================

// CEFR等级配置
const CEFR_LEVELS = ['A1', 'A2', 'B1', 'B2', 'C1'];

const CEFR_INFO = {
    A1: { name: '入门', emoji: '🌱', color: '#27ae60', desc: '基础词汇' },
    A2: { name: '初级', emoji: '🌿', color: '#2ecc71', desc: '初级词汇' },
    B1: { name: '中级', emoji: '🌳', color: '#f39c12', desc: '中级词汇' },
    B2: { name: '中高级', emoji: '🔥', color: '#e67e22', desc: '中高级词汇' },
    C1: { name: '高级', emoji: '⚡', color: '#e74c3c', desc: '高级词汇' }
};

// 音频播放器 - 使用预生成的 WAV 文件
class AudioPlayer {
    constructor(audioBasePath) {
        this.basePath = audioBasePath || 'words/tts_delivery/audio/';
        this.currentAudio = null;
        this.enabled = true;
        this.audioCache = {};
    }

    // 播放单词发音
    playWord(filename) {
        if (!this.enabled || !filename) return;

        // 停止当前正在播放的
        this.stop();

        const path = this.basePath + filename;

        // 尝试从缓存获取
        if (this.audioCache[path]) {
            this.currentAudio = this.audioCache[path];
            this.currentAudio.currentTime = 0;
            this.currentAudio.play().catch(() => { });
            return;
        }

        // 创建新的Audio对象
        const audio = new Audio(path);
        audio.volume = 0.8;
        this.audioCache[path] = audio;
        this.currentAudio = audio;
        audio.play().catch(() => {
            // 如果WAV播放失败，回退到浏览器TTS
            console.warn('WAV播放失败，使用浏览器TTS:', filename);
            this.fallbackTTS(filename.replace('.wav', ''));
        });
    }

    // 浏览器TTS回退
    fallbackTTS(word) {
        if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance(word);
            utterance.lang = 'en-US';
            utterance.rate = 0.8;
            window.speechSynthesis.speak(utterance);
        }
    }

    stop() {
        if (this.currentAudio) {
            this.currentAudio.pause();
            this.currentAudio.currentTime = 0;
        }
        if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel();
        }
    }

    toggle() {
        this.enabled = !this.enabled;
        if (!this.enabled) this.stop();
        return this.enabled;
    }

    // 预加载一批音频（可选，提升体验）
    preload(filenames) {
        filenames.forEach(fn => {
            if (!fn) return;
            const path = this.basePath + fn;
            if (!this.audioCache[path]) {
                const audio = new Audio();
                audio.preload = 'auto';
                audio.src = path;
                this.audioCache[path] = audio;
            }
        });
    }
}

// 音效生成器（游戏音效，保持原有Web Audio API）
class SoundGenerator {
    constructor() {
        this.audioContext = null;
        this.enabled = true;
    }

    _getContext() {
        if (!this.audioContext) {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        }
        return this.audioContext;
    }

    playMergeSound(level) {
        if (!this.enabled) return;
        const ctx = this._getContext();
        const oscillator = ctx.createOscillator();
        const gainNode = ctx.createGain();
        oscillator.connect(gainNode);
        gainNode.connect(ctx.destination);
        oscillator.frequency.value = 220 + (level * 50);
        oscillator.type = 'sine';
        gainNode.gain.setValueAtTime(0.3, ctx.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.3);
        oscillator.start(ctx.currentTime);
        oscillator.stop(ctx.currentTime + 0.3);
    }

    playMoveSound() {
        if (!this.enabled) return;
        const ctx = this._getContext();
        const oscillator = ctx.createOscillator();
        const gainNode = ctx.createGain();
        oscillator.connect(gainNode);
        gainNode.connect(ctx.destination);
        oscillator.frequency.value = 220;
        oscillator.type = 'square';
        gainNode.gain.setValueAtTime(0.1, ctx.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.1);
        oscillator.start(ctx.currentTime);
        oscillator.stop(ctx.currentTime + 0.1);
    }

    playGameOverSound() {
        if (!this.enabled) return;
        const ctx = this._getContext();
        const oscillator = ctx.createOscillator();
        const gainNode = ctx.createGain();
        oscillator.connect(gainNode);
        gainNode.connect(ctx.destination);
        oscillator.frequency.value = 330;
        oscillator.type = 'sawtooth';
        gainNode.gain.setValueAtTime(0.2, ctx.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.5);
        oscillator.start(ctx.currentTime);
        oscillator.stop(ctx.currentTime + 0.5);
    }

    playWinSound() {
        if (!this.enabled) return;
        const ctx = this._getContext();
        const frequencies = [523, 659, 784, 1047];
        frequencies.forEach((freq, i) => {
            const oscillator = ctx.createOscillator();
            const gainNode = ctx.createGain();
            oscillator.connect(gainNode);
            gainNode.connect(ctx.destination);
            oscillator.frequency.value = freq;
            oscillator.type = 'sine';
            const startTime = ctx.currentTime + (i * 0.15);
            gainNode.gain.setValueAtTime(0.2, startTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, startTime + 0.3);
            oscillator.start(startTime);
            oscillator.stop(startTime + 0.3);
        });
    }

    toggle() {
        this.enabled = !this.enabled;
        if (!this.enabled) this.stopBGM(); // 关音效同时也关音乐（或者分开控制）
        return this.enabled;
    }

    // --- 背景音乐 (BGM) 系统 ---
    startBGM() {
        if (!this.enabled) return;

        // 如果已经有音乐在播放，就不用重新创建，直接播放
        if (this.bgmAudio) {
            this.bgmAudio.play().catch(e => console.log('BGM play failed:', e));
            return;
        }

        // 加载 bgm.mp3
        this.bgmAudio = new Audio('bgm.mp3');
        this.bgmAudio.loop = true; // 循环播放
        this.bgmAudio.volume = 0.2; // 默认音量

        this.bgmAudio.play().catch(e => {
            console.warn('BGM Auto-play blocked or file missing:', e);
        });
    }

    stopBGM() {
        if (this.bgmAudio) {
            this.bgmAudio.pause();
            this.bgmAudio.currentTime = 0; // 重置进度（可选，如果只是暂定可以不重置）
        }
    }

    setBGMVolume(val) {
        if (this.bgmAudio) {
            // val 范围 0.0 - 1.0
            // 使用平方曲线 (val * val) 来优化低音量体验
            // 比如滑块在 10% (0.1) 时，实际音量为 1% (0.01)
            const volume = Math.max(0, Math.min(1, val));
            this.bgmAudio.volume = volume * volume;
        }
    }
}

// 词汇管理器
class VocabularyManager {
    constructor() {
        // OXFORD_VOCABULARY 从 oxford_vocabulary.js 加载
        this.allWords = typeof OXFORD_VOCABULARY !== 'undefined' ? OXFORD_VOCABULARY : {};
        this.activeLevels = ['A1']; // 默认只启用A1
        this.wordPool = [];         // 当前活跃的词池
        this.usedWords = new Set();  // 已使用的单词（避免短期重复）
        this.refreshPool();
    }

    // 刷新词池
    refreshPool() {
        this.wordPool = [];
        this.activeLevels.forEach(level => {
            if (this.allWords[level]) {
                this.allWords[level].forEach(w => {
                    this.wordPool.push({ ...w, cefr: level });
                });
            }
        });
        // 洗牌
        this.shuffle(this.wordPool);
        this.usedWords.clear();
    }

    // 设置活跃等级
    setActiveLevels(levels) {
        this.activeLevels = levels.filter(l => CEFR_LEVELS.includes(l));
        if (this.activeLevels.length === 0) this.activeLevels = ['A1'];
        this.refreshPool();
    }

    // 获取随机单词
    getRandomWord() {
        if (this.wordPool.length === 0) return null;

        // 如果大部分单词都用过了，重置
        if (this.usedWords.size >= this.wordPool.length * 0.8) {
            this.usedWords.clear();
        }

        // 找一个没用过的
        let attempts = 0;
        let word;
        do {
            word = this.wordPool[Math.floor(Math.random() * this.wordPool.length)];
            attempts++;
        } while (this.usedWords.has(word.word) && attempts < 50);

        this.usedWords.add(word.word);
        return word;
    }

    // 获取指定等级的单词数量
    getWordCount(level) {
        return this.allWords[level] ? this.allWords[level].length : 0;
    }

    // 获取总活跃单词数
    getActiveWordCount() {
        return this.wordPool.length;
    }

    shuffle(arr) {
        for (let i = arr.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [arr[i], arr[j]] = [arr[j], arr[i]];
        }
    }
}

// 导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { CEFR_LEVELS, CEFR_INFO, AudioPlayer, SoundGenerator, VocabularyManager };
}
