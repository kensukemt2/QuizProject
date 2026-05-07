<template>
  <div class="about">
    <!-- 背景グロー効果 -->
    <div class="background-glow"></div>
    
    <div class="content-container">
      <div class="about-section">
        <h1>運営者情報</h1>
        <p class="about-description">マジカルクイズについてご紹介いたします。</p>
        
        <div class="about-content">
          <!-- サービス概要 -->
          <section class="info-section">
            <h2>サービス概要</h2>
            <div class="service-overview">
              <div class="overview-item">
                <div class="overview-icon">🎯</div>
                <h3>サービス名</h3>
                <p>マジカルクイズ（Magical Quiz）</p>
              </div>
              <div class="overview-item">
                <div class="overview-icon">🌟</div>
                <h3>コンセプト</h3>
                <p>楽しく学べる知識バトル！魔法のようなクイズ体験を提供</p>
              </div>
              <div class="overview-item">
                <div class="overview-icon">🎲</div>
                <h3>特徴</h3>
                <p>多彩なカテゴリー、画像問題、ランキング機能</p>
              </div>
            </div>
          </section>
          
          <!-- 運営者情報 -->
          <section class="info-section">
            <h2>運営者情報</h2>
            <div class="operator-info">
              <div class="info-grid">
                <div class="info-item">
                  <div class="info-label">運営者</div>
                  <div class="info-value">マジカルクイズ運営チーム</div>
                </div>
                <div class="info-item">
                  <div class="info-label">設立</div>
                  <div class="info-value">2024年</div>
                </div>
                <div class="info-item">
                  <div class="info-label">所在地</div>
                  <div class="info-value">東京都</div>
                </div>
                <div class="info-item">
                  <div class="info-label">メール</div>
                  <div class="info-value">contact@magical-quiz.com</div>
                </div>
                <div class="info-item">
                  <div class="info-label">ウェブサイト</div>
                  <div class="info-value">https://magical-quiz.com</div>
                </div>
                <div class="info-item">
                  <div class="info-label">利用規約</div>
                  <div class="info-value">
                    <router-link to="/terms" class="link">利用規約を見る</router-link>
                  </div>
                </div>
              </div>
            </div>
          </section>
          
          <!-- サービスの特徴 -->
          <section class="info-section">
            <h2>サービスの特徴</h2>
            <div class="features">
              <div class="feature-card">
                <div class="feature-icon">📚</div>
                <h3>豊富なカテゴリー</h3>
                <p>数学、英語、理科、地理、歴史など、様々な分野のクイズを用意しています。知識を楽しく身につけることができます。</p>
              </div>
              <div class="feature-card">
                <div class="feature-icon">🖼️</div>
                <h3>画像クイズ対応</h3>
                <p>テキストだけでなく、画像を使ったクイズも充実。視覚的に楽しめるクイズ体験を提供します。</p>
              </div>
              <div class="feature-card">
                <div class="feature-icon">🏆</div>
                <h3>ランキング機能</h3>
                <p>他のユーザーと競い合えるランキング機能。自分の実力を確認し、さらなる向上を目指せます。</p>
              </div>
              <div class="feature-card">
                <div class="feature-icon">📊</div>
                <h3>学習履歴</h3>
                <p>過去のクイズ結果を確認可能。苦手分野を把握して、効率的な学習をサポートします。</p>
              </div>
              <div class="feature-card">
                <div class="feature-icon">👥</div>
                <h3>ゲストモード</h3>
                <p>会員登録なしでもクイズを楽しめるゲストモード。気軽にお試しいただけます。</p>
              </div>
              <div class="feature-card">
                <div class="feature-icon">🎨</div>
                <h3>美しいUI</h3>
                <p>マジカルなデザインで楽しいクイズ体験。直感的で使いやすいインターフェースを提供します。</p>
              </div>
            </div>
          </section>
          
          <!-- 技術情報 -->
          <section class="info-section">
            <h2>技術情報</h2>
            <div class="tech-info">
              <div class="tech-stack">
                <div class="tech-category">
                  <h4>フロントエンド</h4>
                  <div class="tech-tags">
                    <span class="tech-tag">Vue.js 3</span>
                    <span class="tech-tag">Vue Router</span>
                    <span class="tech-tag">Vuex</span>
                    <span class="tech-tag">Axios</span>
                  </div>
                </div>
                <div class="tech-category">
                  <h4>バックエンド</h4>
                  <div class="tech-tags">
                    <span class="tech-tag">Django</span>
                    <span class="tech-tag">Django REST Framework</span>
                    <span class="tech-tag">SQLite</span>
                    <span class="tech-tag">Python</span>
                  </div>
                </div>
                <div class="tech-category">
                  <h4>デプロイ・インフラ</h4>
                  <div class="tech-tags">
                    <span class="tech-tag">Docker</span>
                    <span class="tech-tag">Nginx</span>
                    <span class="tech-tag">AWS</span>
                    <span class="tech-tag">CI/CD</span>
                  </div>
                </div>
              </div>
            </div>
          </section>
          
          <!-- お問い合わせ -->
          <section class="info-section">
            <h2>お問い合わせ</h2>
            <div class="contact-cta">
              <p>ご質問、ご意見、ご要望がございましたら、お気軽にお問い合わせください。</p>
              <div class="cta-buttons">
                <router-link to="/contact" class="cta-btn primary">
                  <span class="btn-icon">📧</span>
                  お問い合わせフォーム
                </router-link>
                <router-link to="/privacy" class="cta-btn secondary">
                  <span class="btn-icon">🔒</span>
                  プライバシーポリシー
                </router-link>
              </div>
            </div>
          </section>
        </div>
        
        <div class="back-to-home">
          <router-link to="/" class="home-btn">
            <span class="btn-icon">🏠</span>
            ホームに戻る
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AboutPage',
  mounted() {
    // ページタイトルを設定
    document.title = '運営者情報 | マジカルクイズ';
  }
}
</script>

<style scoped>
.about {
  min-height: 100vh;
  background: #060608;
  color: #f5f0e8;
  position: relative;
  overflow: hidden;
  padding-bottom: 3rem;
}

.about::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image: radial-gradient(circle, rgba(255,255,255,0.04) 1px, transparent 1px);
  background-size: 24px 24px;
  z-index: 0;
  pointer-events: none;
}

.background-glow {
  position: absolute;
  top: -10%; right: -5%;
  width: 40%;
  height: 130%;
  background: #e8001c;
  transform: skewX(-8deg);
  z-index: 0;
  opacity: 0.6;
}

.content-container {
  position: relative;
  z-index: 2;
  max-width: 900px;
  margin: 0 auto;
  padding: 40px 24px;
}

.about-section h1 {
  font-size: 28px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #f5f0e8;
  text-shadow: 4px 4px 0 #e8001c;
  margin-bottom: 8px;
}
.about-description {
  font-size: 13px;
  color: #555;
  letter-spacing: 0.05em;
  margin-bottom: 32px;
  border-left: 2px solid #e8001c;
  padding-left: 12px;
}

.about-content { display: flex; flex-direction: column; gap: 2px; }

.info-section {
  background: #0e0e12;
  border: 1px solid #1a1a1a;
  border-left: 4px solid #e8001c;
  padding: 24px;
  position: relative;
  overflow: hidden;
}
.info-section:nth-child(even) { border-left-color: #f5e642; }
.info-section:nth-child(3) { border-left-color: #22c55e; }

.info-section::after {
  content: '';
  position: absolute;
  top: 0; right: 0;
  width: 0; height: 0;
  border-style: solid;
  border-width: 0 32px 32px 0;
  border-color: transparent #060608 transparent transparent;
}

.info-section h2 {
  font-size: 16px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #f5f0e8;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #1a1a1a;
}

/* サービス概要グリッド */
.service-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 2px;
}
.overview-item {
  background: rgba(255,255,255,0.02);
  border: 1px solid rgba(255,255,255,0.04);
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.overview-icon { font-size: 20px; }
.overview-item h3 {
  font-size: 12px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #555;
  margin: 0;
}
.overview-item p { font-size: 13px; color: #888; margin: 0; }

/* 機能リスト */
.feature-list { list-style: none; display: flex; flex-direction: column; gap: 6px; padding: 0; }
.feature-list li {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  background: rgba(255,255,255,0.02);
  border: 1px solid rgba(255,255,255,0.03);
  font-size: 13px;
  color: #888;
}
.feature-list li::before {
  content: '▶';
  font-size: 8px;
  color: #e8001c;
  flex-shrink: 0;
}

/* 連絡先 */
.contact-info { display: flex; flex-direction: column; gap: 6px; }
.contact-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  background: rgba(255,255,255,0.02);
  border: 1px solid rgba(255,255,255,0.03);
  font-size: 13px;
  color: #888;
}
.contact-item a { color: #e8001c; text-decoration: none; }
.contact-item a:hover { color: #ff1a35; }

/* 法的情報 */
.legal-info { display: flex; flex-direction: column; gap: 10px; }
.legal-item h4 {
  font-size: 11px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #444;
  margin-bottom: 4px;
}
.legal-item p { font-size: 13px; color: #666; line-height: 1.6; }

@media (max-width: 600px) {
  .service-overview { grid-template-columns: 1fr; }
}
</style>
