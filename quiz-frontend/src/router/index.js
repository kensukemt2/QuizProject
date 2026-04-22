// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router';
import store from '../store';

import HomePage from '../components/Home.vue';
import LoginComponent from '../components/Login.vue';
import RegisterPage from '../components/Register.vue';
import QuizComponent from '../components/Quiz.vue';
import HistoryComponent from '../components/History.vue';
import LeaderboardComponent from '../components/Leaderboard.vue';
import ProfileComponent from '../components/Profile.vue';
import PrivacyPolicy from '../components/PrivacyPolicy.vue';
import Contact from '../components/Contact.vue';
import About from '../components/About.vue';

const routes = [
  {
   path: '/',
   name: 'home',
   component: HomePage
  },
  {
    path: '/login',
    name: 'login',
    component: LoginComponent,
    meta: { guestOnly: true }
  },
  {
    path: '/register',
    name: 'register',
    component: RegisterPage,
    meta: { guestOnly: true }
  },
  {
    path: '/quiz',
    name: 'quiz',
    component: QuizComponent,
    meta: { requiresAuth: true }
  },
  {
    path: '/history',
    name: 'history',
    component: HistoryComponent,
    meta: { requiresAuth: true }
  },
  {
    path: '/leaderboard',
    name: 'leaderboard',
    component: LeaderboardComponent,
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'profile',
    component: ProfileComponent,
    meta: { requiresAuth: true }
  },
  {
    path: '/privacy',
    name: 'privacy',
    component: PrivacyPolicy
  },
  {
    path: '/contact',
    name: 'contact',
    component: Contact
  },
  {
    path: '/about',
    name: 'about',
    component: About
  }
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
});

// このルートには認証が必要
const authRequiredRoutes = ['profile', 'history', 'leaderboard'];

// ゲストモードでもアクセス可能なルート
const guestAccessibleRoutes = ['quiz'];

// ナビゲーションガードを修正
router.beforeEach((to, from, next) => {
  // Vue 3ではrouter.app.$storeではアクセスできない
  // 直接インポートしたstoreを使用
  const isAuthenticated = store.getters['auth/isAuthenticated'];
  const isGuestMode = store.getters['quiz/isGuestMode'] || 
                     localStorage.getItem('quizMode') === 'guest' ||
                     to.query.mode === 'guest';
  
  
  // 認証が必要なルートで未認証の場合
  if (authRequiredRoutes.includes(to.name) && !isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } });
    return;
  }
  
  // ゲストモードでアクセス可能なルートの場合
  if (guestAccessibleRoutes.includes(to.name) && (isGuestMode || isAuthenticated)) {
    // 認証済みユーザーの場合はゲストモードを無効にする
    if (isAuthenticated) {
      store.commit('quiz/SET_GUEST_MODE', false);
      localStorage.removeItem('quizMode');
    } else if (isGuestMode && !store.getters['quiz/isGuestMode']) {
      // ゲストモードフラグをVuexに保存して一貫性を保つ
      store.commit('quiz/SET_GUEST_MODE', true);
    }
    next();
    return;
  }
  
  // それ以外の通常ルートはそのまま遷移
  next();
});

export default router;


