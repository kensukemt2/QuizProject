import axios from 'axios';

const state = {
  stats: null,
  statsLoading: false,
  statsError: null
};

const mutations = {
  SET_STATS(state, stats) {
    state.stats = stats;
  },
  SET_STATS_LOADING(state, loading) {
    state.statsLoading = loading;
  },
  SET_STATS_ERROR(state, error) {
    state.statsError = error;
  }
};

const actions = {
  async fetchStats({ commit, rootGetters }) {
    try {
      commit('SET_STATS_LOADING', true);
      commit('SET_STATS_ERROR', null);
      
      // トークンが存在するか確認
      const token = rootGetters['auth/token'];
      
      if (!token) {
        console.error('認証トークンが見つかりません');
        throw new Error('認証トークンがありません');
      }
      
      console.log('認証トークン:', token.substring(0, 10) + '...');  // デバッグ用（セキュリティのため一部だけ表示）
      
      const response = await axios.get('http://localhost:8000/api/user/stats/', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      });
      
      commit('SET_STATS', response.data);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch user stats:', error);
      
      // より詳細なエラーログ
      if (error.response) {
        console.error('エラーレスポンス:', error.response.status, error.response.data);
      }
      
      commit('SET_STATS_ERROR', 'Failed to fetch user statistics');
      return {
        total_attempts: 0,
        total_categories_played: 0,
        best_category: null,
        avg_percentage: 0
      };
    } finally {
      commit('SET_STATS_LOADING', false);
    }
  }
};

const getters = {
  stats: state => state.stats,
  statsLoading: state => state.statsLoading,
  statsError: state => state.statsError
};

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
};