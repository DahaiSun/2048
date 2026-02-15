class WordGame {
    constructor() {
        this.size = 4;
        this.grid = Array(this.size).fill().map(() => Array(this.size).fill(null));
        this.score = 0;
        this.bestScore = 0;
        this.learnedWords = new Set();
        this.soundGenerator = new SoundGenerator();
        this.audioPlayer = new AudioPlayer('words/tts_delivery/audio/');
        this.vocabManager = new VocabularyManager();
        this.startTime = Date.now();
        this.hasWon = false;
        this.tiles = {};
        this.isMoving = false;
        this.inputSetup = false;
        this.isMusicPlaying = true; // Default Music ON

        // DOM 元素
        this.gameContainer = document.getElementById('game-container');
        this.tileContainer = document.getElementById('tile-container');
        this.scoreDisplay = document.getElementById('score');
        this.bestScoreDisplay = document.getElementById('best-score');
        this.wordCountDisplay = document.getElementById('word-count');
        this.poolCountDisplay = document.getElementById('pool-count');

        // 加载保存的数据
        this.loadProgress();

        // 初始化等级选择器UI
        this.initLevelSelector();

        // 初始化游戏
        this.init();
    }

    initLevelSelector() {
        // 从 localStorage 恢复词书和等级选择
        let savedBook = localStorage.getItem('wordGameActiveBook') || 'oxford_a1';
        let savedLevels = JSON.parse(localStorage.getItem('wordGameActiveLevels') || '["all"]');

        // 向后兼容：旧版 oxford_5000 迁移到拆分后的词书
        if (savedBook === 'oxford_5000') {
            const cefrMap = { 'A1': 'oxford_a1', 'A2': 'oxford_a2', 'B1': 'oxford_b1', 'B2': 'oxford_b2', 'C1': 'oxford_c1' };
            const firstLevel = savedLevels[0] || 'A1';
            savedBook = cefrMap[firstLevel] || 'oxford_a1';
            savedLevels = ['all'];
            localStorage.setItem('wordGameActiveBook', savedBook);
            localStorage.setItem('wordGameActiveLevels', JSON.stringify(savedLevels));
        }

        // 设置词书（不触发 refreshPool，因为还要设等级）
        const books = this.vocabManager.getAvailableBooks();
        if (books[savedBook]) {
            this.vocabManager.activeBookId = savedBook;
        }

        // 设置等级
        this.vocabManager.setActiveLevels(savedLevels);

        // 构建词书选择器 + 等级选择器
        this.buildWordbookSelector();
        this.buildLevelSelector();
        this.updatePoolCount();
    }

    buildWordbookSelector() {
        const container = document.getElementById('wordbook-selector');
        if (!container) return;
        container.innerHTML = '';

        const books = this.vocabManager.getAvailableBooks();
        const activeBookId = this.vocabManager.activeBookId;

        // 按分组排序：oxford → scene → topic → exam → general
        const groupOrder = { oxford: 0, scene: 1, topic: 2, exam: 3, general: 4 };
        const sortedBooks = Object.entries(books).sort((a, b) => {
            return (groupOrder[a[1].group] || 99) - (groupOrder[b[1].group] || 99);
        });

        const bookColors = WordGame.BOOK_COLORS;

        // 分组渲染（每组用 grid 容器实现两列布局）
        let lastGroup = null;
        let gridContainer = null;
        const groupLabels = { oxford: '📖 Oxford 5000', scene: '🎯 场景词书', topic: '🧩 专题词书', exam: '🎓 考试词书', general: '📚 综合词书' };
        sortedBooks.forEach(([id, book]) => {
            if (book.group !== lastGroup) {
                lastGroup = book.group;
                const groupTitle = document.createElement('div');
                groupTitle.className = 'wordbook-group-title';
                groupTitle.textContent = groupLabels[book.group] || '其他';
                container.appendChild(groupTitle);
                gridContainer = document.createElement('div');
                gridContainer.className = 'wordbook-grid';
                container.appendChild(gridContainer);
            }

            const hue = bookColors[id] !== undefined ? bookColors[id] : 210;
            const card = document.createElement('div');
            card.className = 'wordbook-card' + (id === activeBookId ? ' active' : '');
            card.dataset.bookId = id;
            card.style.setProperty('--hue', hue);
            card.innerHTML = `
                <span class="wordbook-emoji">${book.emoji || '📚'}</span>
                <span class="wordbook-name">${book.name}</span>
                <span class="wordbook-count">${book.totalWords}词</span>
            `;
            card.addEventListener('click', () => this.switchWordbook(id));
            gridContainer.appendChild(card);
        });
    }

    switchWordbook(bookId) {
        this.vocabManager.setActiveBook(bookId);
        localStorage.setItem('wordGameActiveBook', bookId);
        localStorage.setItem('wordGameActiveLevels', JSON.stringify([...this.vocabManager.activeLevels]));

        // 重建 UI
        this.buildWordbookSelector();
        this.buildLevelSelector();
        this.updatePoolCount();

        const book = this.vocabManager.getActiveBook();
        this.showToast(`${book.emoji} ${book.name} (${this.vocabManager.getActiveWordCount()}词)`);
    }

    buildLevelSelector() {
        const container = document.getElementById('level-selector');
        if (!container) return;
        container.innerHTML = '';

        const levels = this.vocabManager.getBookLevels();
        const activeBookId = this.vocabManager.activeBookId;

        // 如果只有一个等级（如场景词书的 "all"），显示简要信息
        if (levels.length === 1 && levels[0] === 'all') {
            const info = document.createElement('div');
            info.style.cssText = 'color: #7f8c8d; text-align: center; padding: 8px;';
            info.textContent = '该词书为单级词书，已自动加载全部词汇';
            container.appendChild(info);
            return;
        }

        levels.forEach(levelId => {
            const levelInfo = this.vocabManager.getBookLevelInfo(activeBookId, levelId);
            const btn = document.createElement('button');
            btn.className = 'level-btn';
            btn.dataset.level = levelId;
            btn.innerHTML = levelInfo ? levelInfo.name : levelId;
            btn.title = `${this.vocabManager.getWordCount(levelId)}词`;

            if (this.vocabManager.activeLevels.includes(levelId)) {
                btn.classList.add('active');
            }

            btn.addEventListener('click', () => this.toggleLevel(levelId, btn));
            container.appendChild(btn);
        });
    }

    toggleLevel(level, btn) {
        const currentLevels = [...this.vocabManager.activeLevels];

        if (currentLevels.includes(level)) {
            if (currentLevels.length <= 1) {
                this.showToast('至少保留一个等级！');
                return;
            }
            const idx = currentLevels.indexOf(level);
            currentLevels.splice(idx, 1);
            btn.classList.remove('active');
        } else {
            currentLevels.push(level);
            btn.classList.add('active');
        }

        this.vocabManager.setActiveLevels(currentLevels);
        localStorage.setItem('wordGameActiveLevels', JSON.stringify(currentLevels));
        this.updatePoolCount();

        const activeNames = currentLevels.join('+');
        this.showToast(`词池: ${activeNames} (${this.vocabManager.getActiveWordCount()}词)`);
    }

    updatePoolCount() {
        if (this.poolCountDisplay) {
            this.poolCountDisplay.textContent = this.vocabManager.getActiveWordCount();
        }
    }

    showToast(msg) {
        let toast = document.getElementById('toast');
        if (!toast) {
            toast = document.createElement('div');
            toast.id = 'toast';
            document.body.appendChild(toast);
        }
        toast.textContent = msg;
        toast.classList.add('show');
        clearTimeout(this._toastTimer);
        this._toastTimer = setTimeout(() => toast.classList.remove('show'), 2000);
    }

    init() {
        this.grid = Array(this.size).fill().map(() => Array(this.size).fill(null));
        this.score = 0;
        this.learnedWords = new Set();
        this.startTime = Date.now();
        this.hasWon = false;
        this.tiles = {};
        this.isMoving = false;
        this.tileContainer.innerHTML = '';

        this.addRandomTile();
        this.addRandomTile();
        this.updateScore();

        if (!this.inputSetup) {
            this.setupInput();
            this.inputSetup = true;
        }

        this.updateBestScore();
        this.initAudio();
    }

    restart() {
        this.saveGameStats();
        this.init();
    }

    initAudio() {
        const btn = document.getElementById('music-btn');
        if (this.isMusicPlaying) {
            if (btn) btn.textContent = '🔊 音乐: 开';

            const startAudio = () => {
                this.soundGenerator._getContext().resume().then(() => {
                    this.soundGenerator.startBGM();

                    // Apply BGM volume from settings
                    const bgmVolSlider = document.getElementById('bgm-volume');
                    if (bgmVolSlider) {
                        this.soundGenerator.setBGMVolume(parseFloat(bgmVolSlider.value));
                    }

                    // Apply Word Volume from settings
                    const wordVolSlider = document.getElementById('word-volume');
                    if (wordVolSlider) {
                        const savedWordVol = localStorage.getItem('wordVolume');
                        if (savedWordVol !== null) {
                            wordVolSlider.value = savedWordVol;
                        }
                        this.audioPlayer.setVolume(parseFloat(wordVolSlider.value));
                    }
                });
                document.removeEventListener('click', startAudio);
                document.removeEventListener('keydown', startAudio);
                document.removeEventListener('touchstart', startAudio);
            };

            document.addEventListener('click', startAudio);
            document.addEventListener('keydown', startAudio);
            document.addEventListener('touchstart', startAudio, { passive: true });
        } else {
            if (btn) btn.textContent = '🔇 音乐: 关';
        }
    }

    toggleSound() {
        const sfxEnabled = this.soundGenerator.toggle();
        const ttsEnabled = this.audioPlayer.toggle();
        const btn = document.getElementById('sound-btn');
        btn.textContent = sfxEnabled ? '🔊 音效: 开' : '🔇 音效: 关';
    }

    toggleMusic() {
        if (this.isMusicPlaying) {
            this.soundGenerator.stopBGM();
            this.isMusicPlaying = false;
        } else {
            this.isMusicPlaying = true; // Optimistic update
            this.soundGenerator._getContext().resume().then(() => {
                this.soundGenerator.startBGM();
            }).catch(e => {
                console.error("Audio resume failed", e);
                this.isMusicPlaying = false; // Revert on failure
                this.updateMusicButton();
            });
        }
        this.updateMusicButton();
    }

    updateMusicButton() {
        const btn = document.getElementById('music-btn');
        if (btn) btn.textContent = this.isMusicPlaying ? '🔊 音乐: 开' : '🔇 音乐: 关';
    }

    setMusicVolume(val) {
        this.soundGenerator.setBGMVolume(parseFloat(val));
    }

    setWordVolume(val) {
        const volume = parseFloat(val);
        this.audioPlayer.setVolume(volume);
        localStorage.setItem('wordVolume', volume);
    }

    // 获取一个随机单词用于新方块
    getRandomWord(level = null) {
        if (level === null) {
            level = Math.random() < 0.9 ? 1 : 2;
        }

        const wordData = this.vocabManager.getRandomWord();
        if (!wordData) {
            return {
                word: '?',
                meaning: '',
                cefr: 'A1',
                audio: null,
                level: level,
                value: [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048][level - 1]
            };
        }

        const values = [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048];
        return {
            word: wordData.word,
            meaning: wordData.meaning || '',
            cefr: wordData.cefr,
            audio: wordData.audio,
            level: level,
            value: values[level - 1]
        };
    }

    // 获取随机单词（用于合并后的新方块）
    getRandomWordForMerge() {
        const wordData = this.vocabManager.getRandomWord();
        if (!wordData) {
            return { word: '?', meaning: '', cefr: 'A1', audio: null };
        }
        return wordData;
    }

    // 计算位置（像素）
    getPosition(index) {
        // Dynamic calculation based on grid cell size
        const gridCell = document.querySelector('.grid-cell');
        if (gridCell) {
            const size = gridCell.getBoundingClientRect().width; // Assuming square
            // We need the gap size too. 
            // In standard CSS grid/flex, gap is space between items.
            // Let's assume standard layout: spacing + index * (size + spacing)
            // But we can just read the grid cell's offset from the container?
            // Better: Get the grid container and the specific cell's position relative to it.
            // Actually, since tiles are absolute positioned, we need to match the visual grid.

            // Re-visiting the logic: changing to read positions from the DOM grid cells directly is safer.
            // But we don't have IDs on grid cells usually.
            // Let's rely on the computed styles.

            // However, typical 2048 implementation uses fixed math.
            // Responsive typical approach:

            const gap = 15; // default gap
            // If on mobile, gap might be smaller?

            // Let's try to calculate it dynamically:
            const container = document.getElementById('grid');
            const cells = container.children;
            const singleCell = cells[0];
            // get cell width
            const cellWidth = singleCell.offsetWidth;

            // Gap can be inferred: (ContainerWidth - 4 * CellWidth) / 5
            const containerWidth = container.offsetWidth;
            const calculatedGap = (containerWidth - 4 * cellWidth) / 5;

            return calculatedGap + index * (cellWidth + calculatedGap);
        }

        // Fallback
        return index * 89 + 12;
    }

    // 创建tile DOM元素
    createTileElement(cell) {
        const tile = document.createElement('div');
        const standardCEFR = ['A1', 'A2', 'B1', 'B2', 'C1'];
        const isStandard = standardCEFR.includes(cell.cefr);

        // 标准 CEFR 用原有配色，非标准（all/高频/核心等）用彩虹级别配色
        if (isStandard) {
            tile.className = `tile tile-cefr-${cell.cefr}-${cell.level}`;
        } else {
            tile.className = `tile tile-cefr-all-${cell.level}`;
        }

        tile.id = `tile-${cell.id}`;
        tile.style.left = this.getPosition(cell.y) + 'px';
        tile.style.top = this.getPosition(cell.x) + 'px';

        const meaningDisplay = cell.meaning || '';
        const badgeLabel = isStandard ? cell.cefr : '';
        tile.innerHTML = `
            ${badgeLabel ? `<div class="tile-cefr-badge cefr-${cell.cefr}">${badgeLabel}</div>` : ''}
            <div class="tile-word">${cell.word}</div>
            <div class="tile-meaning">${meaningDisplay}</div>
            <div class="tile-level">${cell.value}</div>
        `;

        tile.addEventListener('click', () => this.playWordAudio(cell));

        return tile;
    }

    playWordAudio(cell, forceTTS = false) {
        if (!forceTTS && cell.audio) {
            this.audioPlayer.playWord(cell.audio);
        } else {
            this.audioPlayer.fallbackTTS(cell.word);
        }
    }

    addRandomTile() {
        const empty = [];
        for (let i = 0; i < this.size; i++) {
            for (let j = 0; j < this.size; j++) {
                if (!this.grid[i][j]) empty.push({ x: i, y: j });
            }
        }

        if (empty.length > 0) {
            const pos = empty[Math.floor(Math.random() * empty.length)];
            const wordData = this.getRandomWord();
            const cell = {
                ...wordData,
                x: pos.x,
                y: pos.y,
                id: Date.now() + Math.random()
            };

            this.grid[pos.x][pos.y] = cell;

            const tileElement = this.createTileElement(cell);
            tileElement.classList.add('tile-new');
            this.tileContainer.appendChild(tileElement);
            this.tiles[cell.id] = tileElement;

            this.learnedWords.add(cell.word);

            // 新方块出现时自动朗读
            this.playWordAudio(cell);

            setTimeout(() => {
                if (tileElement && tileElement.parentElement) {
                    tileElement.classList.remove('tile-new');
                }
            }, 200);

            return true;
        }
        return false;
    }

    updateScore() {
        this.scoreDisplay.textContent = this.score;
        this.wordCountDisplay.textContent = this.learnedWords.size;

        if (this.score > this.bestScore) {
            this.bestScore = this.score;
            this.bestScoreDisplay.textContent = this.bestScore;
            this.saveBestScore();
        }
    }

    updateBestScore() {
        this.bestScoreDisplay.textContent = this.bestScore;
    }

    move(direction) {
        if (this.isMoving) return;

        const vector = {
            'up': { x: -1, y: 0 },
            'down': { x: 1, y: 0 },
            'left': { x: 0, y: -1 },
            'right': { x: 0, y: 1 }
        }[direction];

        const positions = this.buildTraversals(direction);
        let moved = false;
        const mergedTiles = [];
        const newTiles = [];

        for (let i = 0; i < this.size; i++) {
            for (let j = 0; j < this.size; j++) {
                if (this.grid[i][j]) {
                    this.grid[i][j].mergedFrom = null;
                }
            }
        }

        positions.x.forEach(x => {
            positions.y.forEach(y => {
                const cell = this.grid[x][y];
                if (!cell) return;

                const result = this.findFarthestPosition({ x, y }, vector);
                const next = this.grid[result.next.x] && this.grid[result.next.x][result.next.y];

                if (next && next.value === cell.value && !next.mergedFrom) {
                    const newValue = cell.value * 2;
                    const newLevel = cell.level + 1;
                    // const randomWordData = this.getRandomWordForMerge(); // 不再获取新单词

                    const merged = {
                        word: cell.word,           // 保持原单词
                        meaning: cell.meaning,     // 保持原释义
                        cefr: cell.cefr,           // 保持原CEFR
                        audio: cell.audio,         // 保持原音频
                        level: newLevel,
                        value: newValue,
                        x: result.next.x,
                        y: result.next.y,
                        id: Date.now() + Math.random(),
                        mergedFrom: [cell, next]
                    };

                    this.grid[result.next.x][result.next.y] = merged;
                    this.grid[x][y] = null;

                    const tileElement = this.tiles[cell.id];
                    if (tileElement) {
                        const targetX = this.getPosition(result.next.y);
                        const targetY = this.getPosition(result.next.x);
                        const currentX = this.getPosition(y);
                        const currentY = this.getPosition(x);
                        tileElement.style.transform = `translate(${targetX - currentX}px, ${targetY - currentY}px)`;
                    }

                    this.score += newValue;
                    moved = true;
                    mergedTiles.push(cell.id, next.id);
                    newTiles.push(merged);

                    if (newValue === 2048 && !this.hasWon) {
                        this.hasWon = true;
                        setTimeout(() => {
                            this.soundGenerator.playWinSound();
                            alert('🎉 恭喜你达到2048！你可以继续挑战更高分数！');
                        }, 600);
                    }
                } else if (result.farthest.x !== x || result.farthest.y !== y) {
                    this.grid[result.farthest.x][result.farthest.y] = cell;
                    this.grid[x][y] = null;
                    cell.x = result.farthest.x;
                    cell.y = result.farthest.y;

                    const tileElement = this.tiles[cell.id];
                    if (tileElement) {
                        const targetX = this.getPosition(result.farthest.y);
                        const targetY = this.getPosition(result.farthest.x);
                        const currentX = this.getPosition(y);
                        const currentY = this.getPosition(x);
                        tileElement.style.transform = `translate(${targetX - currentX}px, ${targetY - currentY}px)`;
                    }
                    moved = true;
                }
            });
        });

        if (moved) {
            this.isMoving = true;
            this.soundGenerator.playMoveSound();

            setTimeout(() => {
                mergedTiles.forEach(id => {
                    if (this.tiles[id]) {
                        this.tiles[id].remove();
                        delete this.tiles[id];
                    }
                });

                newTiles.forEach(cell => {
                    const tileElement = this.createTileElement(cell);
                    tileElement.classList.add('tile-merged');
                    this.tileContainer.appendChild(tileElement);
                    this.tiles[cell.id] = tileElement;
                    this.learnedWords.add(cell.word);

                    this.soundGenerator.playMergeSound(cell.level);

                    // 合并时不再朗读
                    // setTimeout(() => {
                    //    this.playWordAudio(cell, true);
                    // }, 200);

                    setTimeout(() => {
                        if (tileElement && tileElement.parentElement) {
                            tileElement.classList.remove('tile-merged');
                        }
                    }, 300);
                });

                for (let i = 0; i < this.size; i++) {
                    for (let j = 0; j < this.size; j++) {
                        const cell = this.grid[i][j];
                        if (cell && this.tiles[cell.id]) {
                            const tileElement = this.tiles[cell.id];
                            tileElement.style.transition = 'none';
                            tileElement.style.left = this.getPosition(j) + 'px';
                            tileElement.style.top = this.getPosition(i) + 'px';
                            tileElement.style.transform = '';
                            tileElement.offsetHeight;
                            tileElement.style.transition = '';
                        }
                    }
                }

                this.addRandomTile();
                this.updateScore();
                this.checkGameOver();
                this.isMoving = false;
            }, 150);
        }
    }

    buildTraversals(direction) {
        const traversals = { x: [], y: [] };
        for (let pos = 0; pos < this.size; pos++) {
            traversals.x.push(pos);
            traversals.y.push(pos);
        }
        if (direction === 'right') traversals.y = traversals.y.reverse();
        if (direction === 'down') traversals.x = traversals.x.reverse();
        return traversals;
    }

    findFarthestPosition(cell, vector) {
        let previous;
        do {
            previous = cell;
            cell = { x: previous.x + vector.x, y: previous.y + vector.y };
        } while (this.withinBounds(cell) && !this.grid[cell.x][cell.y]);
        return { farthest: previous, next: cell };
    }

    withinBounds(position) {
        return position.x >= 0 && position.x < this.size &&
            position.y >= 0 && position.y < this.size;
    }

    checkGameOver() {
        for (let i = 0; i < this.size; i++) {
            for (let j = 0; j < this.size; j++) {
                if (!this.grid[i][j]) return;
                const neighbors = [
                    { x: i + 1, y: j }, { x: i - 1, y: j },
                    { x: i, y: j + 1 }, { x: i, y: j - 1 }
                ];
                for (let n of neighbors) {
                    if (this.withinBounds(n) && this.grid[n.x][n.y] &&
                        this.grid[n.x][n.y].value === this.grid[i][j].value) {
                        return;
                    }
                }
            }
        }

        this.soundGenerator.playGameOverSound();
        this.saveGameStats();

        document.getElementById('final-score').textContent = this.score;
        document.getElementById('final-words').textContent = this.learnedWords.size;

        const allTimeStats = JSON.parse(localStorage.getItem('wordGameStats') || '{}');
        const isNewRecord = this.score > (allTimeStats.allTimeBest || 0);
        document.getElementById('new-record').style.display = isNewRecord ? 'block' : 'none';

        document.getElementById('game-over-modal').classList.add('active');
    }

    setupInput() {
        document.addEventListener('keydown', (e) => {
            const keys = {
                'ArrowUp': 'up', 'ArrowDown': 'down',
                'ArrowLeft': 'left', 'ArrowRight': 'right',
                'w': 'up', 'W': 'up',
                's': 'down', 'S': 'down',
                'a': 'left', 'A': 'left',
                'd': 'right', 'D': 'right'
            };
            if (keys[e.key]) {
                e.preventDefault();
                this.move(keys[e.key]);
            }
        });

        let touchStartX = 0;
        let touchStartY = 0;

        // Use document to capture swipes anywhere on screen
        document.addEventListener('touchstart', (e) => {
            touchStartX = e.touches[0].clientX;
            touchStartY = e.touches[0].clientY;
        }, { passive: true });

        document.addEventListener('touchmove', (e) => {
            // Only prevent default when actually swiping (not just touching)
            const dx = Math.abs(e.touches[0].clientX - touchStartX);
            const dy = Math.abs(e.touches[0].clientY - touchStartY);
            if (dx > 10 || dy > 10) {
                e.preventDefault();
            }
        }, { passive: false });

        document.addEventListener('touchend', (e) => {
            const touchEndX = e.changedTouches[0].clientX;
            const touchEndY = e.changedTouches[0].clientY;
            const dx = touchEndX - touchStartX;
            const dy = touchEndY - touchStartY;
            const minSwipe = 30; // Reduced threshold for better responsiveness

            if (Math.abs(dx) > Math.abs(dy) && Math.abs(dx) > minSwipe) {
                this.move(dx > 0 ? 'right' : 'left');
            } else if (Math.abs(dy) > minSwipe) {
                this.move(dy > 0 ? 'down' : 'up');
            }
        });
        // Mouse Swipe Support
        let mouseStartX = 0;
        let mouseStartY = 0;
        let isMouseDown = false;

        document.addEventListener('mousedown', (e) => {
            isMouseDown = true;
            mouseStartX = e.clientX;
            mouseStartY = e.clientY;
        });

        document.addEventListener('mouseup', (e) => {
            if (!isMouseDown) return;
            isMouseDown = false;

            if (!this.hasWon && !this.isGameOver()) {
                const mouseEndX = e.clientX;
                const mouseEndY = e.clientY;
                const dx = mouseEndX - mouseStartX;
                const dy = mouseEndY - mouseStartY;
                const minSwipe = 50;

                if (Math.abs(dx) > Math.abs(dy) && Math.abs(dx) > minSwipe) {
                    this.move(dx > 0 ? 'right' : 'left');
                } else if (Math.abs(dy) > minSwipe) {
                    this.move(dy > 0 ? 'down' : 'up');
                }
            }
        });
    }

    saveBestScore() {
        localStorage.setItem('wordGameBestScore', this.bestScore);
    }

    saveGameStats() {
        const stats = JSON.parse(localStorage.getItem('wordGameStats') || '{}');
        const playTime = Math.round((Date.now() - this.startTime) / 1000 / 60);

        stats.totalGames = (stats.totalGames || 0) + 1;
        stats.totalWordsArray = stats.totalWordsArray || [];
        this.learnedWords.forEach(word => {
            if (!stats.totalWordsArray.includes(word)) {
                stats.totalWordsArray.push(word);
            }
        });
        stats.allTimeBest = Math.max(stats.allTimeBest || 0, this.score);
        stats.totalTime = (stats.totalTime || 0) + playTime;

        localStorage.setItem('wordGameStats', JSON.stringify(stats));
    }

    loadProgress() {
        this.bestScore = parseInt(localStorage.getItem('wordGameBestScore') || '0');
    }

    showStats() {
        const stats = JSON.parse(localStorage.getItem('wordGameStats') || '{}');

        document.getElementById('total-games').textContent = stats.totalGames || 0;
        document.getElementById('total-words').textContent = (stats.totalWordsArray || []).length;
        document.getElementById('all-time-best').textContent = stats.allTimeBest || 0;
        document.getElementById('total-time').textContent = (stats.totalTime || 0) + ' 分钟';

        const wordsList = document.getElementById('learned-words-list');
        wordsList.innerHTML = '';
        const allWords = stats.totalWordsArray || [];
        allWords.sort().forEach(word => {
            const badge = document.createElement('span');
            badge.className = 'word-badge';
            badge.textContent = word;
            badge.onclick = () => {
                // 尝试找到音频文件
                this.audioPlayer.playWord(word + '.wav');
            };
            badge.style.cursor = 'pointer';
            badge.title = '点击朗读';
            wordsList.appendChild(badge);
        });

        document.getElementById('stats-modal').classList.add('active');
    }

    showSettings() {
        document.getElementById('settings-modal').classList.add('active');
    }

    showLevels() {
        document.getElementById('levels-modal').classList.add('active');
    }

    resetStats() {
        if (confirm('确定要清除所有统计数据吗？此操作不可恢复！')) {
            localStorage.removeItem('wordGameStats');
            localStorage.removeItem('wordGameBestScore');
            this.bestScore = 0;
            this.updateBestScore();
            alert('统计数据已清除！');
            document.getElementById('stats-modal').classList.remove('active');
        }
    }
}

// 每个词书的独特色相 (HSL hue)
WordGame.BOOK_COLORS = {
    'oxford_a1': 120, 'oxford_a2': 160, 'oxford_b1': 200, 'oxford_b2': 30, 'oxford_c1': 270,
    'scene_food': 15, 'scene_clothing': 340, 'scene_home': 25,
    'scene_transport': 200, 'scene_health': 160, 'scene_shopping': 330,
    'scene_nature': 140, 'scene_entertainment': 280, 'scene_travel': 190,
    'scene_work': 215, 'scene_school': 45, 'scene_social': 350,
    'scene_fitness': 10, 'scene_music': 270, 'scene_animals': 35,
    'scene_plants': 130, 'scene_festivals': 0, 'scene_cooking': 20,
    'scene_law': 230,
    'topic_tech': 205, 'topic_social_media': 260, 'topic_gaming': 290,
    'topic_finance': 40, 'topic_marketing': 320, 'topic_film': 300,
    'topic_medical': 170, 'topic_science': 185, 'topic_space': 240,
    'topic_art': 310, 'topic_politics': 220, 'topic_math': 55,
    'topic_environment': 145, 'topic_psychology': 275, 'topic_sports': 120,
    'topic_architecture': 30, 'topic_ai': 250,
    'cet4': 38, 'cet6': 22,
};

// 初始化游戏
let game;
window.addEventListener('DOMContentLoaded', () => {
    game = new WordGame();
});
