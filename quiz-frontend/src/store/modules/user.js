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
      
      // authモジュールからトークンを取得
      const token = rootGetters['auth/token'];
      
      const response = await axios.get('http://localhost:8000/api/user/stats/', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      commit('SET_STATS', response.data);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch user stats:', error);
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