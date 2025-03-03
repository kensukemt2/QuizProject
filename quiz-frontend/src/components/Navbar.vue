<!-- src/components/Navbar.vue -->
<template>
    <nav class="navbar">
      <div class="logo">
        <router-link to="/">4択クイズアプリ</router-link>
      </div>
      <div class="nav-links">
        <template v-if="isAuthenticated">
          <router-link to="/quiz">クイズ</router-link>
          <router-link to="/history">履歴</router-link>
          <router-link to="/leaderboard">ランキング</router-link>
          <span class="user-info">{{ user.username }}さん</span>
          <button class="logout-btn" @click="handleLogout">ログアウト</button>
        </template>
        <template v-else>
          <router-link to="/login">ログイン</router-link>
          <router-link to="/register">登録</router-link>
        </template>
      </div>
      
    </nav>
  </template>
  
  <script>
  import { mapGetters, mapActions } from 'vuex';
  
  export default {
    name: 'SiteNavigation',
    computed: {
      ...mapGetters('auth', ['isAuthenticated', 'user'])
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