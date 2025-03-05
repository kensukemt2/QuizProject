import axios from 'axios';
import store from '../store';
import router from '../router';

const api = axios.create({
  baseURL: 'http://localhost:8000',
});

// リクエストインターセプター
api.interceptors.request.use(
  config => {
    const token = store.state.auth.token;
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// レスポンスインターセプター
api.interceptors.response.use(
  response => response,
  async error => {
    // 401エラー（認証エラー）の場合
    if (error.response && error.response.status === 401) {
      // ログアウト処理
      await store.dispatch('auth/logout');
      // ログインページへリダイレクト
      router.push('/login');
    }
    return Promise.reject(error);
  }
);

export default api;