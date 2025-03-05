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
  }
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
});

// ナビゲーションガード
router.beforeEach((to, from, next) => {
  const isAuthenticated = store.getters['auth/isAuthenticated'];
  
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!isAuthenticated) {
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      });
    } else {
      next();
    }
  } else {
    next();
  }
});

export default router;


