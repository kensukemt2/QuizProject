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
  position: relative;
  background: linear-gradient(to bottom right, #3B82F6, #1E40AF);
  overflow: hidden;
  color: #FFFFFF;
  font-family: Arial, sans-serif;
  padding: 2rem 0;
}

/* 背景グロー効果 */
.background-glow {
  position: absolute;
  top: -100px;
  left: 0;
  right: 0;
  width: 600px;
  height: 600px;
  margin: 0 auto;
  background: radial-gradient(circle, rgba(147, 197, 253, 0.6) 0%, rgba(30, 64, 175, 0) 70%);
  z-index: 0;
}

/* グリッド線 */
.about::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    linear-gradient(to right, rgba(147, 197, 253, 0.2) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(147, 197, 253, 0.2) 1px, transparent 1px);
  background-size: 200px 200px;
  z-index: 1;
}

.content-container {
  position: relative;
  z-index: 2;
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 1rem;
}

.about-section {
  background-color: rgba(59, 130, 246, 0.7);
  border-radius: 20px;
  padding: 2rem;
  position: relative;
  overflow: hidden;
  border-top: 5px solid rgba(249, 115, 22, 0.7);
}

.about-section h1 {
  text-align: center;
  margin-bottom: 1rem;
  font-size: 2.5rem;
  color: white;
}

.about-description {
  text-align: center;
  margin-bottom: 2rem;
  color: #DBEAFE;
  line-height: 1.6;
}

.about-content {
  background-color: rgba(255, 255, 255, 0.05);
  border-radius: 15px;
  padding: 2rem;
  margin-bottom: 2rem;
}

.info-section {
  margin-bottom: 3rem;
}

.info-section:last-child {
  margin-bottom: 0;
}

.info-section h2 {
  color: #F97316;
  font-size: 1.5rem;
  margin-bottom: 1.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid rgba(249, 115, 22, 0.3);
}

/* サービス概要 */
.service-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.overview-item {
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 1.5rem;
  text-align: center;
  transition: transform 0.3s ease;
}

.overview-item:hover {
  transform: translateY(-3px);
}

.overview-icon {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.overview-item h3 {
  color: #FACC15;
  margin-bottom: 0.5rem;
}

.overview-item p {
  color: #DBEAFE;
  line-height: 1.5;
}

/* 運営者情報 */
.operator-info {
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 2rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background-color: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
}

.info-label {
  color: #FACC15;
  font-weight: bold;
  min-width: 100px;
}

.info-value {
  color: #DBEAFE;
  text-align: right;
}

.link {
  color: #93C5FD;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

/* サービスの特徴 */
.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.feature-card {
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 1.5rem;
  transition: transform 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-3px);
}

.feature-icon {
  font-size: 2rem;
  margin-bottom: 1rem;
}

.feature-card h3 {
  color: #FACC15;
  margin-bottom: 1rem;
}

.feature-card p {
  color: #DBEAFE;
  line-height: 1.6;
}

/* 技術情報 */
.tech-info {
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 2rem;
}

.tech-stack {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
}

.tech-category h4 {
  color: #FACC15;
  margin-bottom: 1rem;
}

.tech-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.tech-tag {
  background-color: rgba(249, 115, 22, 0.2);
  color: #FED7AA;
  padding: 0.3rem 0.8rem;
  border-radius: 15px;
  font-size: 0.875rem;
  border: 1px solid rgba(249, 115, 22, 0.3);
}

/* お問い合わせCTA */
.contact-cta {
  text-align: center;
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 2rem;
}

.contact-cta p {
  margin-bottom: 2rem;
  color: #DBEAFE;
  line-height: 1.6;
}

.cta-buttons {
  display: flex;
  justify-content: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.cta-btn {
  display: inline-flex;
  align-items: center;
  padding: 0.8rem 2rem;
  border-radius: 25px;
  font-weight: bold;
  text-decoration: none;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.cta-btn.primary {
  background: linear-gradient(to bottom, #F97316, #EA580C);
  color: white;
}

.cta-btn.secondary {
  background: linear-gradient(to bottom, #3B82F6, #2563EB);
  color: white;
}

.cta-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 5px;
  background-color: rgba(255, 255, 255, 0.3);
  border-radius: 25px 25px 0 0;
}

.cta-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

/* ホームボタン */
.back-to-home {
  text-align: center;
}

.home-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.8rem 2rem;
  background: linear-gradient(to bottom, #10B981, #059669);
  color: white;
  text-decoration: none;
  border-radius: 25px;
  font-weight: bold;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.home-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 5px;
  background-color: rgba(255, 255, 255, 0.3);
  border-radius: 25px 25px 0 0;
}

.home-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.btn-icon {
  margin-right: 0.5rem;
  font-size: 1.2rem;
}

/* レスポンシブデザイン */
@media (max-width: 768px) {
  .about-section {
    padding: 1.5rem;
  }
  
  .about-section h1 {
    font-size: 2rem;
  }
  
  .about-content {
    padding: 1.5rem;
  }
  
  .service-overview,
  .features {
    grid-template-columns: 1fr;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .tech-stack {
    grid-template-columns: 1fr;
  }
  
  .cta-buttons {
    flex-direction: column;
    align-items: center;
  }
}

@media (max-width: 480px) {
  .about {
    padding: 1rem 0;
  }
  
  .content-container {
    padding: 0 0.5rem;
  }
  
  .about-section {
    padding: 1rem;
  }
  
  .about-section h1 {
    font-size: 1.8rem;
  }
  
  .about-content {
    padding: 1rem;
  }
  
  .info-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .info-value {
    text-align: left;
  }
}
</style>