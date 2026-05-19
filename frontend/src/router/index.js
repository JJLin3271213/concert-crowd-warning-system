import { createRouter, createWebHistory } from 'vue-router'
import UserView from '../views/UserView.vue'
import AdminView from '../views/AdminView.vue'

const routes = [
  { path: '/', name: 'user', component: UserView },
  { 
    path: '/admin', 
    name: 'admin', 
    component: AdminView,
    beforeEnter: (to, from, next) => {
      const token = localStorage.getItem('token')
      if (token) {
        next()
      } else {
        alert('请先登录')
        next('/')
      }
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router