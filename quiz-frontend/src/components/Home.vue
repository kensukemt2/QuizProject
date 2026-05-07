<template>
  <div class="home">
    <!-- 背景グロー効果 -->
    <div class="background-glow"></div>
    
    <div class="header">
      <div class="logo">
        <div class="logo-box">Q</div>
        <h1>マジカルクイズ</h1>
      </div>
      
      <!-- ユーザーバッジ（ログイン中のみ表示） -->
      <div v-if="isAuthenticated" class="user-badge">
        {{ user.username.charAt(0).toUpperCase() }}{{ user.username.charAt(1).toUpperCase() }}
      </div>
    </div>
    
    <div class="content-container">
      <div class="hero-section">
        <div class="character">
          <div class="face"></div>
          <div class="eye left"></div>
          <div class="eye-pupil left"></div>
          <div class="eye right"></div>
          <div class="eye-pupil right"></div>
          <div class="mouth"></div>
          <div class="hair"></div>
        </div>
        
        <div class="hero-text">
          <h2>マジカルクイズワールド</h2>
          <p>４つの選択肢から正解を見つけよう！魔法の知識バトル！</p>
        </div>
        
        <!-- ログイン済みユーザー向け -->
        <div v-if="isAuthenticated" class="authenticated-options">
          <button class="btn primary-btn" @click="startQuiz">クイズを始める</button>
          <div class="user-stats">
            <p>こんにちは、{{ user.username }}さん</p>
            <p>これまでの挑戦回数: {{ userStats.total_attempts || 0 }}</p>
          </div>
        </div>
        
        <!-- ゲストユーザー向け -->
        <div v-else class="guest-options">
          <button class="btn primary-btn" @click="startGuestQuiz">ゲストとしてクイズを始める</button>
          <button class="btn secondary-btn" @click="goToLogin">ログインする</button>
        </div>
      </div>
      
      <!-- カテゴリーセクション -->
      <div class="category-section">
        <h3>クイズカテゴリ</h3>
        <div class="category-underline"></div>
        
        <!-- ローディング状態 -->
        <div v-if="loading" class="loading-categories">
          <p>カテゴリをロード中...</p>
        </div>
        
        <!-- エラー表示 -->
        <div v-else-if="error" class="error-message">
          <p>{{ error }}</p>
          <button @click="fetchCategories" class="retry-btn">再読み込み</button>
        </div>
        
        <!-- カテゴリ一覧 -->
        <div v-else-if="categories && categories.length > 0" class="categories">
          <div 
            v-for="category in categories" 
            :key="category.id"
            :class="['category-card', category.colorClass]"
          >
            <div class="category-line"></div>
            <h4>{{ category.name }}</h4>
            <div class="category-icon">{{ category.icon }}</div>
            <button class="category-btn" @click="startCategoryQuiz(category.id)">挑戦する</button>
          </div>
        </div>
        
        <!-- カテゴリがない場合 -->
        <div v-else class="no-categories">
          <p>現在利用可能なカテゴリーはありません。</p>
        </div>
      </div>
      
      <!-- ゲスト向け情報 -->
      <div v-if="!isAuthenticated" class="guest-info">
        <h3>ログインするメリット</h3>
        <ul>
          <li>クイズの成績を保存できる</li>
          <li>ランキングに参加できる</li>
          <li>履歴から過去の回答を確認できる</li>
          <li>カスタマイズされたクイズに挑戦できる</li>
        </ul>
      </div>
      
      <!-- リーダーボードプレビュー -->
      <div class="leaderboard-preview">
        <div class="leaderboard-container">
          <template v-if="leaderboardLoading">
            <span class="loading-indicator">ランキング取得中...</span>
          </template>
          <template v-else>
            <template v-for="(user, index) in leaderboard" :key="index">
              <span :class="['rank', getRankClass(index)]">{{ index + 1 }}</span>
              <span>{{ user.username || '名無し' }} - {{ formatPercentage(user.avg_percentage || 0) }}</span>
            </template>
            <span v-if="isAuthenticated" class="all-rankings" @click="$router.push('/leaderboard')">全ランキング ▶</span>

<style scoped>
/* ── ベース ── */
.home {
  min-height: 100vh;
  position: relative;
  background: #060608;
  overflow: hidden;
  color: #f5f0e8;
  padding-bottom: 3rem;
}

/* 斜めスラッシュ背景 */
.background-glow {
  position: absolute;
  top: -10%; right: -5%;
  width: 52%;
  height: 130%;
  background: #e8001c;
  transform: skewX(-8deg);
  z-index: 0;
}

/* グリッドパターン */
.home::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image:
    radial-gradient(circle, rgba(255,255,255,0.05) 1px, transparent 1px);
  background-size: 24px 24px;
  z-index: 1;
  pointer-events: none;
}

/* 黄色ライン */
.home::after {
  content: '';
  position: absolute;
  top: -10%; right: 44%;
  width: 4px;
  height: 130%;
  background: #f5e642;
  transform: skewX(-8deg);
  z-index: 2;
  opacity: 0.8;
}

/* ── ヘッダー ── */
.header {
  height: 56px;
  background: rgba(6,6,8,0.95);
  display: flex;
  justify-content: space-between;
  align-items: stretch;
  padding: 0;
  border-bottom: 2px solid #1a1a1a;
  position: relative;
  z-index: 10;
}

.header::after {
  content: '';
  position: absolute;
  bottom: 0; left: 0; right: 0;
  height: 2px;
  background: #e8001c;
}

.logo {
  display: flex;
  align-items: center;
  padding: 0 24px;
}

.logo-box {
  width: 40px;
  height: 40px;
  background: #e8001c;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  font-weight: 700;
  clip-path: polygon(0 0, 85% 0, 100% 100%, 0 100%);
  border-radius: 0;
  margin-right: 0;
  padding-right: 6px;
}

.logo h1 {
  color: #f5f0e8;
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  padding-left: 14px;
  margin: 0;
}

.user-badge {
  width: 28px;
  height: 28px;
  background: #e8001c;
  clip-path: polygon(0 0, 100% 0, 100% 70%, 85% 100%, 0 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  color: #fff;
  margin: auto 24px auto 0;
}

/* ── コンテンツエリア ── */
.content-container {
  position: relative;
  z-index: 3;
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 1.5rem;
}

/* ── ヒーローセクション ── */
.hero-section {
  background: rgba(14,14,18,0.85);
  border: 1px solid #1a1a1a;
  border-left: 4px solid #e8001c;
  padding: 2.5rem 2rem;
  margin-top: 2.5rem;
  position: relative;
  text-align: center;
  overflow: hidden;
}

.hero-section::before {
  content: '';
  position: absolute;
  top: 0; right: 0;
  width: 0; height: 0;
  border-style: solid;
  border-width: 0 40px 40px 0;
  border-color: transparent #060608 transparent transparent;
}

/* キャラクターは非表示（ペルソナスタイルでは不要） */
.character { display: none; }

.hero-text { margin-bottom: 2rem; }

.hero-text h2 {
  font-size: clamp(2rem, 5vw, 3.2rem);
  line-height: 1;
  letter-spacing: 0.04em;
  color: #f5f0e8;
  text-shadow: 4px 4px 0 #e8001c;
  margin-bottom: 1rem;
}

.hero-text p {
  font-size: 13px;
  color: rgba(245,240,232,0.5);
  line-height: 1.8;
  max-width: 500px;
  margin: 0 auto;
  border-left: 2px solid #e8001c;
  padding-left: 12px;
  text-align: left;
}

/* ボタン */
.btn {
  padding: 0.9rem 2.4rem;
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.18em;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
  clip-path: polygon(0 0, 100% 0, 95% 100%, 0 100%);
}

.primary-btn {
  background: #f5e642;
  color: #060608;
  animation: none;
  position: relative;
}

.primary-btn::before { content: '▶ '; font-size: 10px; }
.primary-btn:hover { background: #f5f0e8; transform: translateX(4px); }

.secondary-btn {
  background: transparent;
  color: #555;
  border: 1px solid #333;
  margin-left: 1rem;
  clip-path: polygon(0 0, 100% 0, 95% 100%, 0 100%);
}
.secondary-btn:hover { border-color: #666; color: #f5f0e8; }

/* ユーザー統計 */
.user-stats {
  display: flex;
  gap: 1px;
  margin-top: 1.5rem;
  max-width: 360px;
  margin-left: auto;
  margin-right: auto;
}

.user-stats p {
  flex: 1;
  background: rgba(245,240,232,0.04);
  border: 1px solid rgba(245,240,232,0.08);
  border-top: 2px solid #e8001c;
  padding: 12px 14px;
  margin: 0;
  font-size: 12px;
  color: #888;
  letter-spacing: 0.05em;
  border-left: none;
}

.user-stats p:first-child { border-left: 1px solid rgba(245,240,232,0.08); }

/* ── カテゴリセクション ── */
.category-section {
  margin-top: 3rem;
}

.category-section h3 {
  font-size: 20px;
  letter-spacing: 0.08em;
  color: #f5f0e8;
  margin-bottom: 0;
  text-transform: uppercase;
  display: inline-block;
}

.category-underline {
  width: 100%;
  height: 1px;
  background: #1a1a1a;
  margin: 8px 0 1.5rem;
  position: relative;
}

.category-underline::before {
  content: '';
  position: absolute;
  left: 0; top: 0;
  width: 160px;
  height: 2px;
  background: #e8001c;
  margin-top: -0.5px;
}

.categories {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 2px;
}

.category-card {
  background: #0e0e12;
  border: 1px solid #111;
  padding: 1.5rem;
  text-align: left;
  position: relative;
  height: auto;
  min-height: 120px;
  transition: all 0.2s;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.category-card::after {
  content: '';
  position: absolute;
  right: 18px;
  bottom: 14px;
  font-family: 'Reggae One', sans-serif;
  font-size: 48px;
  color: rgba(255,255,255,0.03);
  line-height: 1;
}

.category-card:hover {
  background: #111118;
  transform: translateX(4px);
  border-color: rgba(255,255,255,0.1);
}

/* カテゴリーの左ライン（colorClassを使用） */
.category-line {
  position: absolute;
  top: 0; left: 0; bottom: 0;
  width: 3px;
  transform: scaleY(0);
  transform-origin: bottom;
  transition: transform 0.25s;
}

.category-card:hover .category-line { transform: scaleY(1); }

.category-card.anime .category-line  { background: #e8001c; }
.category-card.game  .category-line  { background: #22c55e; }
.category-card.manga .category-line  { background: #f5e642; }
.category-card.pop   .category-line  { background: #60a5fa; }

.category-card h4 {
  font-size: 14px;
  letter-spacing: 0.04em;
  color: #f5f0e8;
  margin: 0;
}

.category-icon {
  width: 44px;
  height: 44px;
  background: #0a0a0e;
  border: 1px solid #1e1e22;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 700;
  color: #f5f0e8;
  clip-path: polygon(0 0, 100% 0, 80% 100%, 0 100%);
  position: relative;
  flex-shrink: 0;
  letter-spacing: 0;
}

.category-card.anime .category-icon {
.category-card.game  .category-icon {
.category-card.manga .category-icon {
.category-card.pop   .category-icon {

.category-btn {
  background: transparent;
  border: 1px solid #333;
  color: #555;
  padding: 6px 14px;
  font-size: 11px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  cursor: pointer;
  transition: all 0.15s;
  clip-path: polygon(0 0, 100% 0, 90% 100%, 0 100%);
  align-self: flex-start;
  margin-top: auto;
}

.category-btn:hover { border-color: #e8001c; color: #e8001c; }

/* ローディング・エラー */
.loading-categories, .error-message, .no-categories {
  text-align: center;
  padding: 2rem;
  background: #0e0e12;
  border: 1px solid #1a1a1a;
  border-left: 4px solid #e8001c;
  color: #888;
}
.error-message { border-left-color: #ef4444; color: #ef4444; }
.retry-btn {
  background: transparent;
  border: 1px solid #333;
  color: #555;
  padding: 8px 18px;
  cursor: pointer;
  margin-top: 0.5rem;
  transition: all 0.15s;
}
.retry-btn:hover { border-color: #e8001c; color: #e8001c; }

/* ゲスト情報 */
.guest-info {
  margin-top: 3rem;
  background: #0e0e12;
  border: 1px solid #1a1a1a;
  border-left: 4px solid #f5e642;
  padding: 1.5rem;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.guest-info h3 {
  color: #f5e642;
  font-size: 14px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  margin-bottom: 1rem;
}

.guest-info ul { text-align: left; padding-left: 1.2rem; }
.guest-info li { margin: 0.4rem 0; color: #555; font-size: 13px; }

/* リーダーボード */
.leaderboard-preview {
  margin-top: 2.5rem;
  display: flex;
  justify-content: center;
}

.leaderboard-container {
  background: #0e0e12;
  border: 1px solid #1a1a1a;
  border-top: 2px solid #e8001c;
  padding: 10px 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  color: #555;
  clip-path: polygon(0 0, 100% 0, 98% 100%, 0 100%);
}

.rank {
  width: 16px; height: 16px;
  border-radius: 0;
  text-align: center;
  line-height: 16px;
  font-size: 11px;
  font-weight: 700;
  clip-path: polygon(0 0, 100% 0, 85% 100%, 0 100%);
}
.rank.gold   { background: #FFD700; color: #060608; }
.rank.silver { background: #C0C0C0; color: #060608; }
.rank.bronze { background: #CD7F32; color: #060608; }

.all-rankings { color: #e8001c; cursor: pointer; margin-left: auto; letter-spacing: 0.05em; }
.all-rankings:hover { color: #ff1a35; }
.loading-indicator { color: #555; }

/* ゲストオプション */
.guest-options { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; }
.authenticated-options { display: flex; flex-direction: column; align-items: center; }

/* レスポンシブ */
@media (max-width: 768px) {
  .header { padding: 0; }
  .logo h1 { font-size: 14px; }
  .hero-text h2 { font-size: 1.6rem; }
  .hero-text p { font-size: 12px; }
  .secondary-btn { margin-left: 0; margin-top: 0.5rem; }
  .categories { grid-template-columns: 1fr 1fr; }
  .leaderboard-container { flex-wrap: wrap; justify-content: center; }
}

@media (max-width: 480px) {
  .categories { grid-template-columns: 1fr; }
}
</style>
