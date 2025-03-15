import axios from 'axios';
import store from '../store';
import router from '../router';

const api = axios.create({
  baseURL: process.env.VUE_APP_API_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// トークン認証のインターセプター
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;  // Token から Bearer に変更
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// レスポンスインターセプター
api.interceptors.response.use(
  response => response,
  async error => {
    // 401エラー（認証エラー）の場合
    if (error.response && error.response.status === 401) {
      // リーダーボードなど一部のAPIでは認証エラーを記録するだけ
      console.warn('認証エラーが発生しました。トークンが無効または期限切れの可能性があります。');
      
      // リーダーボードページの場合は自動ログアウトしない
      const isLeaderboardPage = router.currentRoute.value.path === '/leaderboard';
      if (!isLeaderboardPage) {
        // ログアウト処理
        await store.dispatch('auth/logout');
        // ログインページへリダイレクト
        router.push('/login');
      }
    }
    return Promise.reject(error);
  }
);

export default api;