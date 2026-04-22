<!-- src/components/Navbar.vue -->
<template>
  <nav class="navbar" aria-label="メインナビゲーション">
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
        
        <div class="dropdown" @mouseover="showDropdown = true" @mouseleave="showDropdown = false" @keydown.escape="showDropdown = false">
          <button type="button" class="nav-btn dropdown-trigger" aria-haspopup="true" :aria-expanded="showDropdown.toString()" @click="showDropdown = !showDropdown" @keydown.enter.prevent="showDropdown = !showDropdown" @keydown.space.prevent="showDropdown = !showDropdown">
            情報
            <span class="dropdown-arrow" aria-hidden="true">▼</span>
          </button>
          <div class="dropdown-menu" :class="{ 'show': showDropdown }" role="menu">
            <router-link to="/about" class="dropdown-item" role="menuitem">運営者情報</router-link>
            <router-link to="/contact" class="dropdown-item" role="menuitem">お問い合わせ</router-link>
            <router-link to="/privacy" class="dropdown-item" role="menuitem">プライバシーポリシー</router-link>
          </div>
        </div>
        
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
        <div class="dropdown" @mouseover="showGuestDropdown = true" @mouseleave="showGuestDropdown = false" @keydown.escape="showGuestDropdown = false">
          <button type="button" class="nav-btn dropdown-trigger" aria-haspopup="true" :aria-expanded="showGuestDropdown.toString()" @click="showGuestDropdown = !showGuestDropdown" @keydown.enter.prevent="showGuestDropdown = !showGuestDropdown" @keydown.space.prevent="showGuestDropdown = !showGuestDropdown">
            情報
            <span class="dropdown-arrow" aria-hidden="true">▼</span>
          </button>
          <div class="dropdown-menu" :class="{ 'show': showGuestDropdown }" role="menu">
            <router-link to="/about" class="dropdown-item" role="menuitem">運営者情報</router-link>
            <router-link to="/contact" class="dropdown-item" role="menuitem">お問い合わせ</router-link>
            <router-link to="/privacy" class="dropdown-item" role="menuitem">プライバシーポリシー</router-link>
          </div>
        </div>
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
  data() {
    return {
      showDropdown: false,
      showGuestDropdown: false
    }
  },
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
  position: sticky;
  top: 0;
  z-index: 1000;
  overflow: visible;
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
  z-index: 0;
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
  z-index: 0;
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
  z-index: 1;
}

/* ロゴ部分 */
.logo {
  display: flex;
  align-items: center;
  position: relative;
  z-index: 10;
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
  z-index: 10;
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

/* ドロップダウンメニュー */
.dropdown {
  position: relative;
  display: inline-block;
  z-index: 20;
}

.dropdown-trigger {
  display: flex;
  align-items: center;
  cursor: pointer;
  border: none;
  font-family: inherit;
  font-size: inherit;
}

.dropdown-arrow {
  margin-left: 5px;
  font-size: 12px;
  transition: transform 0.3s ease;
}

.dropdown:hover .dropdown-arrow {
  transform: rotate(180deg);
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  min-width: 180px;
  background-color: #1E40AF;
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
  opacity: 0;
  visibility: hidden;
  transform: translateY(-10px);
  transition: all 0.3s ease;
  z-index: 9999;
  border: 1px solid rgba(147, 197, 253, 0.2);
  margin-top: 0;
}

.dropdown-menu.show {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}

.dropdown-item {
  display: block;
  padding: 12px 16px;
  color: #93C5FD;
  text-decoration: none;
  font-size: 14px;
  transition: all 0.3s ease;
  border-bottom: 1px solid rgba(147, 197, 253, 0.1);
}

.dropdown-item:last-child {
  border-bottom: none;
}

.dropdown-item:hover {
  background-color: #3B82F6;
  color: white;
  padding-left: 20px;
}

.dropdown-item:first-child {
  border-radius: 10px 10px 0 0;
}

.dropdown-item:last-child {
  border-radius: 0 0 10px 10px;
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
  
  .dropdown-menu {
    position: static;
    opacity: 1;
    visibility: visible;
    transform: none;
    box-shadow: none;
    border: none;
    background-color: transparent;
    margin-top: 10px;
  }
  
  .dropdown-item {
    background-color: #1E40AF;
    margin-bottom: 5px;
    border-radius: 10px;
    border: none;
  }
}
</style>