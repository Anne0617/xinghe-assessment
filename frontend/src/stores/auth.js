import { defineStore } from 'pinia'
import api from '@/api'
export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    user: JSON.parse(localStorage.getItem('user') || 'null')
  }),
  getters: {
    isLoggedIn: (s) => !!s.token,
    isSuperAdmin: (s) => s.user?.role === 'super_admin'
  },
  actions: {
    async login(username, password) {
      const r = await api.post('/token/', { username, password })
      this.token = r.data.access; localStorage.setItem('token', this.token)
      const ur = await api.get('/me/'); this.user = ur.data
      localStorage.setItem('user', JSON.stringify(this.user))
    },
    logout() { this.token = ''; this.user = null; localStorage.removeItem('token'); localStorage.removeItem('user') }
  }
})
