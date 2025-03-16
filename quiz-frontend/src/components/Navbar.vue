<!-- src/components/Navbar.vue -->
<template>
  <nav class="navbar">
    <div class="grid-lines"></div>
    <div class="glow-effect"></div>
    
    <div class="logo">
      <div class="logo-box">
        <span class="logo-text">Q</span>
      </div>
      <router-link to="/" class="site-name">マジカルクイズ</router-link>
    </div>
    
    <div class="nav-links">
      <template v-if="isAuthenticated">
        <router-link to="/quiz" class="nav-link" active-class="nav-active">
          <div class="nav-btn">クイズ</div>
        </router-link>
        <router-link to="/history" class="nav-link" active-class="nav-active">
          <div class="nav-btn">履歴</div>
        </router-link>
        <router-link to="/leaderboard" class="nav-link" active-class="nav-active">
          <div class="nav-btn">ランキング</div>
        </router-link>
        <router-link to="/profile" class="nav-link" active-class="nav-active">
          <div class="nav-btn">プロフィール</div>
        </router-link>
        
        <div class="user-profile" v-if="currentUser">
          <div class="user-avatar">
            {{ currentUser.username ? currentUser.username.charAt(0).toUpperCase() : 'U' }}
          </div>
          <span class="user-name">{{ currentUser.username }}さん</span>
        </div>
        
        <button class="logout-btn" @click="handleLogout">
          ログアウト
          <span class="logout-icon">⟲</span>
        </button>
      </template>
      <template v-else>
        <router-link to="/login" class="auth-btn login">ログイン</router-link>
        <router-link to="/register" class="auth-btn register">登録</router-link>
      </template>
    </div>
  </nav>
</template>

<script>
import { mapGetters, mapActions } from 'vuex';

export default {
  name: 'SiteNavigation',
  computed: {
    ...mapGetters('auth', ['isAuthenticated', 'currentUser'])
  },
  methods: {
    ...mapActions('auth', ['logout']),
    async handleLogout() {
      await this.logout();
      this.$router.push('/login');
    }
  }
};
</script>

<style scoped>
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  height: 70px;
  background-color: #2563EB;
  color: white;
  position: relative;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

/* グリッド線の装飾 */
.grid-lines {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background:
    linear-gradient(90deg, transparent 19%, rgba(147, 197, 253, 0.1) 20%, transparent 21%),
    linear-gradient(90deg, transparent 39%, rgba(147, 197, 253, 0.1) 40%, transparent 41%),
    linear-gradient(90deg, transparent 59%, rgba(147, 197, 253, 0.1) 60%, transparent 61%),
    linear-gradient(90deg, transparent 79%, rgba(147, 197, 253, 0.1) 80%, transparent 81%);
  background-size: 20% 100%;
  z-index: 1;
  pointer-events: none;
}

/* グロー効果 */
.glow-effect {
  position: absolute;
  top: -80px;
  left: 50%;
  transform: translateX(-50%);
  width: 300px;
  height: 200px;
  background: radial-gradient(circle, rgba(147, 197, 253, 0.4) 0%, rgba(30, 64, 175, 0) 70%);
  z-index: 1;
  pointer-events: none;
}

/* オレンジの線 */
.navbar::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background-color: #F97316;
  z-index: 2;
}

/* ロゴ部分 */
.logo {
  display: flex;
  align-items: center;
  position: relative;
  z-index: 2;
}

.logo-box {
  width: 40px;
  height: 40px;
  background-color: #F97316;
  border-radius: 10px;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-right: 10px;
}

.logo-text {
  font-weight: bold;
  font-size: 26px;
  color: #FFFFFF;
}

.site-name {
  font-size: 24px;
  font-weight: bold;
  color: #FFFFFF;
  text-decoration: none;
}

/* ナビゲーションリンク */
.nav-links {
  display: flex;
  align-items: center;
  gap: 10px;
  position: relative;
  z-index: 2;
}

.nav-link {
  text-decoration: none;
}

.nav-btn {
  padding: 8px 15px;
  border-radius: 15px;
  background-color: #1E40AF;
  color: #93C5FD;
  font-size: 14px;
  transition: all 0.3s;
}

.nav-active .nav-btn {
  background-color: #3B82F6;
  color: white;
  box-shadow: 0 0 0 2px #93C5FD;
}

.nav-btn:hover {
  background-color: #3B82F6;
  color: white;
  transform: translateY(-2px);
}

/* ユーザープロフィール */
.user-profile {
  display: flex;
  align-items: center;
  margin-left: 15px;
}

.user-avatar {
  width: 40px;
  height: 40px;
  background-color: #F97316;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  font-weight: bold;
  font-size: 18px;
  color: white;
  border: 2px solid white;
  margin-right: 8px;
}

.user-name {
  font-size: 14px;
  color: white;
}

/* ログアウトボタン */
.logout-btn {
  padding: 8px 15px;
  border: none;
  border-radius: 15px;
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  margin-left: 15px;
}

.logout-btn:hover {
  background-color: rgba(255, 255, 255, 0.3);
}

.logout-icon {
  margin-left: 5px;
  font-size: 16px;
}

/* 認証ボタン（ログイン前） */
.auth-btn {
  padding: 8px 20px;
  border-radius: 15px;
  font-size: 14px;
  text-decoration: none;
  transition: all 0.3s;
}

.auth-btn.login {
  background-color: #1E40AF;
  color: white;
}

.auth-btn.register {
  background-color: #F97316;
  color: white;
}

.auth-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

/* レスポンシブデザイン */
@media (max-width: 768px) {
  .navbar {
    flex-direction: column;
    height: auto;
    padding: 15px;
  }
  
  .logo {
    margin-bottom: 15px;
  }
  
  .nav-links {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .user-profile {
    margin: 10px 0;
  }
  
  .logout-btn {
    margin: 10px 0;
  }
}
</style>