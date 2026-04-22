<template>
  <div class="contact">
    <!-- 背景グロー効果 -->
    <div class="background-glow"></div>
    
    <div class="content-container">
      <div class="contact-section">
        <h1>お問い合わせ</h1>
        <p class="contact-description">マジカルクイズに関するご質問、ご意見、ご要望がございましたら、下記フォームよりお気軽にお問い合わせください。</p>
        
        <!-- 成功メッセージ -->
        <div v-if="submitted" class="success-message">
          <div class="success-icon">✓</div>
          <h3>お問い合わせを受け付けました</h3>
          <p>ご連絡いただき、ありがとうございます。内容を確認の上、可能な限り迅速にご返信いたします。</p>
          <button @click="resetForm" class="new-inquiry-btn">新しいお問い合わせ</button>
        </div>
        
        <!-- お問い合わせフォーム -->
        <form v-else @submit.prevent="submitForm" class="contact-form">
          <div class="form-group">
            <label for="name" class="required">お名前</label>
            <input 
              type="text" 
              id="name" 
              v-model="form.name" 
              :class="{ 'error': errors.name }"
              placeholder="山田太郎"
              required
            />
            <span v-if="errors.name" class="error-message">{{ errors.name }}</span>
          </div>
          
          <div class="form-group">
            <label for="email" class="required">メールアドレス</label>
            <input 
              type="email" 
              id="email" 
              v-model="form.email" 
              :class="{ 'error': errors.email }"
              placeholder="example@email.com"
              required
            />
            <span v-if="errors.email" class="error-message">{{ errors.email }}</span>
          </div>
          
          <div class="form-group">
            <label for="category">お問い合わせ種別</label>
            <select id="category" v-model="form.category">
              <option value="general">一般的なお問い合わせ</option>
              <option value="bug">バグ報告</option>
              <option value="feature">機能要望</option>
              <option value="content">コンテンツに関して</option>
              <option value="account">アカウントに関して</option>
              <option value="other">その他</option>
            </select>
          </div>
          
          <div class="form-group">
            <label for="subject" class="required">件名</label>
            <input 
              type="text" 
              id="subject" 
              v-model="form.subject" 
              :class="{ 'error': errors.subject }"
              placeholder="お問い合わせの件名をご入力ください"
              required
            />
            <span v-if="errors.subject" class="error-message">{{ errors.subject }}</span>
          </div>
          
          <div class="form-group">
            <label for="message" class="required">お問い合わせ内容</label>
            <textarea 
              id="message" 
              v-model="form.message" 
              :class="{ 'error': errors.message }"
              placeholder="お問い合わせ内容を詳しくご記入ください"
              rows="6"
              required
            ></textarea>
            <span v-if="errors.message" class="error-message">{{ errors.message }}</span>
            <div class="character-count">{{ form.message.length }}/1000文字</div>
          </div>
          
          <div class="form-group checkbox-group">
            <label class="checkbox-label">
              <input 
                type="checkbox" 
                v-model="form.consent"
                :class="{ 'error': errors.consent }"
                required
              />
              <span class="checkmark"></span>
              <router-link to="/privacy" target="_blank" class="privacy-link">プライバシーポリシー</router-link>に同意します
            </label>
            <span v-if="errors.consent" class="error-message">{{ errors.consent }}</span>
          </div>
          
          <div class="form-actions">
            <button type="submit" class="submit-btn" :disabled="submitting">
              <span v-if="submitting" class="spinner"></span>
              {{ submitting ? '送信中...' : '送信する' }}
            </button>
          </div>
        </form>
        
        <div class="contact-info">
          <h3>その他のご連絡方法</h3>
          <div class="info-cards">
            <div class="info-card">
              <div class="info-icon">📧</div>
              <h4>メール</h4>
              <p>contact@magical-quiz.com</p>
            </div>
            <div class="info-card">
              <div class="info-icon">⏰</div>
              <h4>対応時間</h4>
              <p>平日 9:00-18:00<br>（土日祝日を除く）</p>
            </div>
            <div class="info-card">
              <div class="info-icon">📱</div>
              <h4>SNS</h4>
              <p>@MagicalQuiz<br>（Twitter/X）</p>
            </div>
          </div>
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
  name: 'ContactPage',
  data() {
    return {
      form: {
        name: '',
        email: '',
        category: 'general',
        subject: '',
        message: '',
        consent: false
      },
      errors: {},
      submitting: false,
      submitted: false
    }
  },
  mounted() {
    // ページタイトルを設定
    document.title = 'お問い合わせ | マジカルクイズ';
  },
  methods: {
    validateForm() {
      this.errors = {};
      
      if (!this.form.name.trim()) {
        this.errors.name = 'お名前を入力してください';
      }
      
      if (!this.form.email.trim()) {
        this.errors.email = 'メールアドレスを入力してください';
      } else if (!this.isValidEmail(this.form.email)) {
        this.errors.email = '有効なメールアドレスを入力してください';
      }
      
      if (!this.form.subject.trim()) {
        this.errors.subject = '件名を入力してください';
      }
      
      if (!this.form.message.trim()) {
        this.errors.message = 'お問い合わせ内容を入力してください';
      } else if (this.form.message.length > 1000) {
        this.errors.message = 'お問い合わせ内容は1000文字以内で入力してください';
      }
      
      if (!this.form.consent) {
        this.errors.consent = 'プライバシーポリシーに同意してください';
      }
      
      return Object.keys(this.errors).length === 0;
    },
    
    isValidEmail(email) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      return emailRegex.test(email);
    },
    
    async submitForm() {
      if (!this.validateForm()) {
        return;
      }
      
      this.submitting = true;
      
      try {
        // 実際のAPIエンドポイントがある場合はここで送信
        // await this.sendContactForm(this.form);
        
        // デモ用の遅延
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // ローカルストレージに保存（デモ用）
        const contacts = JSON.parse(localStorage.getItem('contactForms') || '[]');
        contacts.push({
          ...this.form,
          timestamp: new Date().toISOString(),
          id: Date.now()
        });
        localStorage.setItem('contactForms', JSON.stringify(contacts));
        
        this.submitted = true;
        
      } catch (error) {
        console.error('お問い合わせの送信に失敗しました:', error);
        alert('送信に失敗しました。時間をおいて再度お試しください。');
      } finally {
        this.submitting = false;
      }
    },
    
    resetForm() {
      this.form = {
        name: '',
        email: '',
        category: 'general',
        subject: '',
        message: '',
        consent: false
      };
      this.errors = {};
      this.submitted = false;
      this.submitting = false;
    }
  },
  watch: {
    'form.message'(newValue) {
      if (newValue.length > 1000) {
        this.form.message = newValue.substring(0, 1000);
      }
    }
  }
}
</script>

<style scoped>
.contact {
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
.contact::before {
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
  max-width: 800px;
  margin: 0 auto;
  padding: 0 1rem;
}

.contact-section {
  background-color: rgba(59, 130, 246, 0.7);
  border-radius: 20px;
  padding: 2rem;
  position: relative;
  overflow: hidden;
  border-top: 5px solid rgba(249, 115, 22, 0.7);
}

.contact-section h1 {
  text-align: center;
  margin-bottom: 1rem;
  font-size: 2.5rem;
  color: white;
}

.contact-description {
  text-align: center;
  margin-bottom: 2rem;
  color: #DBEAFE;
  line-height: 1.6;
}

/* 成功メッセージ */
.success-message {
  background-color: rgba(16, 185, 129, 0.2);
  border: 2px solid #10B981;
  border-radius: 15px;
  padding: 2rem;
  text-align: center;
  margin-bottom: 2rem;
}

.success-icon {
  width: 60px;
  height: 60px;
  background-color: #10B981;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1rem;
  font-size: 2rem;
  color: white;
  font-weight: bold;
}

.success-message h3 {
  color: #10B981;
  margin-bottom: 1rem;
}

.new-inquiry-btn {
  background: linear-gradient(to bottom, #3B82F6, #2563EB);
  color: white;
  border: none;
  padding: 0.8rem 2rem;
  border-radius: 25px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 1rem;
}

.new-inquiry-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

/* フォームスタイル */
.contact-form {
  background-color: rgba(255, 255, 255, 0.05);
  border-radius: 15px;
  padding: 2rem;
  margin-bottom: 2rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #DBEAFE;
  font-weight: bold;
}

.required::after {
  content: ' *';
  color: #F97316;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.8rem;
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  background-color: rgba(255, 255, 255, 0.1);
  color: white;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.form-group input::placeholder,
.form-group textarea::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #F97316;
  background-color: rgba(255, 255, 255, 0.15);
}

.form-group input.error,
.form-group select.error,
.form-group textarea.error {
  border-color: #EF4444;
}

.error-message {
  display: block;
  color: #FCA5A5;
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

.character-count {
  text-align: right;
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.6);
  margin-top: 0.25rem;
}

/* チェックボックス */
.checkbox-group {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
}

.checkbox-label {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  cursor: pointer;
  line-height: 1.5;
}

.checkbox-label input[type="checkbox"] {
  width: auto;
  margin: 0;
}

.privacy-link {
  color: #FACC15;
  text-decoration: none;
}

.privacy-link:hover {
  text-decoration: underline;
}

.form-actions {
  text-align: center;
  margin-top: 2rem;
}

.submit-btn {
  background: linear-gradient(to bottom, #F97316, #EA580C);
  color: white;
  border: none;
  padding: 1rem 3rem;
  border-radius: 25px;
  font-size: 1.1rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.submit-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 5px;
  background-color: rgba(255, 255, 255, 0.3);
  border-radius: 25px 25px 0 0;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid transparent;
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* お問い合わせ情報 */
.contact-info {
  background-color: rgba(255, 255, 255, 0.05);
  border-radius: 15px;
  padding: 2rem;
  margin-bottom: 2rem;
}

.contact-info h3 {
  text-align: center;
  margin-bottom: 1.5rem;
  color: #F97316;
}

.info-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.info-card {
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 1.5rem;
  text-align: center;
  transition: transform 0.3s ease;
}

.info-card:hover {
  transform: translateY(-3px);
}

.info-icon {
  font-size: 2rem;
  margin-bottom: 1rem;
}

.info-card h4 {
  color: #FACC15;
  margin-bottom: 0.5rem;
}

.info-card p {
  color: #DBEAFE;
  line-height: 1.5;
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
  .contact-section {
    padding: 1.5rem;
  }
  
  .contact-section h1 {
    font-size: 2rem;
  }
  
  .contact-form {
    padding: 1.5rem;
  }
  
  .info-cards {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .contact {
    padding: 1rem 0;
  }
  
  .content-container {
    padding: 0 0.5rem;
  }
  
  .contact-section {
    padding: 1rem;
  }
  
  .contact-section h1 {
    font-size: 1.8rem;
  }
  
  .contact-form {
    padding: 1rem;
  }
  
  .submit-btn {
    padding: 0.8rem 2rem;
    font-size: 1rem;
  }
}
</style>