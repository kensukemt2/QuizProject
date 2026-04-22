<template>
  <div class="privacy-policy">
    <!-- 背景グロー効果 -->
    <div class="background-glow"></div>
    
    <div class="content-container">
      <div class="policy-section">
        <h1>プライバシーポリシー</h1>
        <p class="last-updated">最終更新日：2024年12月</p>
        
        <div class="policy-content">
          <section class="policy-item">
            <h2>1. 個人情報の収集について</h2>
            <p>マジカルクイズでは、サービスの提供にあたり以下の個人情報を収集する場合があります：</p>
            <ul>
              <li>ユーザー名</li>
              <li>メールアドレス</li>
              <li>クイズの回答履歴</li>
              <li>サービス利用状況</li>
            </ul>
          </section>
          
          <section class="policy-item">
            <h2>2. 個人情報の利用目的</h2>
            <p>収集した個人情報は以下の目的で利用いたします：</p>
            <ul>
              <li>サービスの提供・運営</li>
              <li>ユーザーサポート</li>
              <li>サービスの改善・新機能の開発</li>
              <li>利用状況の分析</li>
              <li>重要なお知らせの配信</li>
            </ul>
          </section>
          
          <section class="policy-item">
            <h2>3. 個人情報の第三者提供</h2>
            <p>当サービスは、法令に基づく場合を除き、事前の同意なく個人情報を第三者に提供することはありません。</p>
          </section>
          
          <section class="policy-item">
            <h2>4. 個人情報の管理</h2>
            <p>個人情報の漏洩、滅失、毀損等を防止するため、適切な安全管理措置を実施しています。</p>
          </section>
          
          <section class="policy-item">
            <h2>5. Cookie（クッキー）について</h2>
            <p>当サービスでは、サービスの利便性向上のためCookieを使用する場合があります。Cookieの使用を希望されない場合は、ブラウザの設定で無効にすることができます。</p>
          </section>
          
          <section class="policy-item">
            <h2>6. ゲストモード</h2>
            <p>ゲストモードでご利用の場合、クイズの結果はブラウザのローカルストレージに一時的に保存され、サーバーには送信されません。</p>
          </section>
          
          <section class="policy-item">
            <h2>7. アクセス解析ツール</h2>
            <p>当サービスでは、サービス向上のためアクセス解析を行う場合があります。これらのツールは匿名化された情報を収集し、個人を特定するものではありません。</p>
          </section>
          
          <section class="policy-item">
            <h2>8. プライバシーポリシーの変更</h2>
            <p>本プライバシーポリシーは、必要に応じて変更することがあります。変更後のプライバシーポリシーは、本ページに掲載した時点で効力を生じるものとします。</p>
          </section>
          
          <section class="policy-item">
            <h2>9. お問い合わせ</h2>
            <p>本プライバシーポリシーに関するお問い合わせは、<router-link to="/contact" class="contact-link">お問い合わせフォーム</router-link>よりご連絡ください。</p>
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
  name: 'PrivacyPolicy',
  mounted() {
    // ページタイトルを設定
    document.title = 'プライバシーポリシー | マジカルクイズ';
  }
}
</script>

<style scoped>
.privacy-policy {
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
.privacy-policy::before {
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

/* コンテンツコンテナ */
.content-container {
  position: relative;
  z-index: 2;
  max-width: 800px;
  margin: 0 auto;
  padding: 0 1rem;
}

.policy-section {
  background-color: rgba(59, 130, 246, 0.7);
  border-radius: 20px;
  padding: 2rem;
  position: relative;
  overflow: hidden;
  border-top: 5px solid rgba(249, 115, 22, 0.7);
}

.policy-section h1 {
  text-align: center;
  margin-bottom: 0.5rem;
  font-size: 2.5rem;
  color: white;
}

.last-updated {
  text-align: center;
  margin-bottom: 2rem;
  color: #DBEAFE;
  font-style: italic;
}

.policy-content {
  background-color: rgba(255, 255, 255, 0.05);
  border-radius: 15px;
  padding: 2rem;
  margin-bottom: 2rem;
}

.policy-item {
  margin-bottom: 2.5rem;
}

.policy-item:last-child {
  margin-bottom: 0;
}

.policy-item h2 {
  color: #F97316;
  font-size: 1.3rem;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid rgba(249, 115, 22, 0.3);
}

.policy-item p {
  line-height: 1.7;
  margin-bottom: 1rem;
  color: #DBEAFE;
}

.policy-item ul {
  padding-left: 2rem;
  margin-bottom: 1rem;
}

.policy-item li {
  margin-bottom: 0.5rem;
  color: #DBEAFE;
  line-height: 1.6;
}

.contact-link {
  color: #FACC15;
  text-decoration: none;
  font-weight: bold;
}

.contact-link:hover {
  text-decoration: underline;
}

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
  .policy-section {
    padding: 1.5rem;
  }
  
  .policy-section h1 {
    font-size: 2rem;
  }
  
  .policy-content {
    padding: 1.5rem;
  }
  
  .policy-item h2 {
    font-size: 1.2rem;
  }
}

@media (max-width: 480px) {
  .privacy-policy {
    padding: 1rem 0;
  }
  
  .content-container {
    padding: 0 0.5rem;
  }
  
  .policy-section {
    padding: 1rem;
  }
  
  .policy-section h1 {
    font-size: 1.8rem;
  }
  
  .policy-content {
    padding: 1rem;
  }
  
  .policy-item ul {
    padding-left: 1.5rem;
  }
}
</style>