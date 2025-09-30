import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AdminMaintenance from '@/views/AdminMaintenance.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: () => import('@/views/Home.vue'),
      meta: { requiresAuth: false }
    },
            {
              path: '/library',
              name: 'Library',
              component: () => import('@/views/Library.vue'),
              meta: { requiresAuth: true }
            },
            {
              path: '/tv-series',
              name: 'TVSeries',
              component: () => import('@/views/TVSeries.vue'),
              meta: { requiresAuth: true }
            },
            {
              path: '/playlists',
              name: 'Playlists',
              component: () => import('@/views/Playlists.vue'),
              meta: { requiresAuth: true }
            },
            {
              path: '/player/:id',
              name: 'MediaPlayer',
              component: () => import('@/views/MediaPlayer.vue'),
              meta: { requiresAuth: true }
            },
            {
              path: '/analytics',
              name: 'Analytics',
              component: () => import('@/views/Analytics.vue'),
              meta: { requiresAuth: true }
            },
            {
              path: '/settings',
              name: 'Settings',
              component: () => import('@/views/Settings.vue'),
              meta: { requiresAuth: true }
            },
            {
              path: '/admin/maintenance',
              name: 'AdminMaintenance',
              component: AdminMaintenance,
              meta: { requiresAuth: true, requiresAdmin: true }
            },
            {
              path: '/test',
              name: 'StreamingTest',
              component: () => import('@/views/StreamingTest.vue'),
              meta: { requiresAuth: true }
            },
            {
              path: '/login',
              name: 'Login',
              component: () => import('@/views/Login.vue'),
              meta: { requiresAuth: false }
            },
    {
      path: '/:pathMatch(.*)*',
      name: 'NotFound',
      redirect: '/'
    }
  ]
})

// Navigation guards
router.beforeEach(async (to, _from, next) => {
  const authStore = useAuthStore()
  
  // Initialize auth store if not already done
  if (authStore.token && !authStore.user) {
    try {
      await authStore.initialize()
    } catch (error) {
      console.error('Auth initialization failed during navigation:', error)
    }
  }
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    console.log('Navigation blocked: Authentication required for', to.path)
    next('/login')
  } else if (to.meta.requiresAdmin && !authStore.isAdmin) {
    console.log('Navigation blocked: Admin access required for', to.path)
    next('/')
  } else if ((to.name === 'Login' || to.name === 'Register') && authStore.isAuthenticated) {
    console.log('Navigation redirect: Already authenticated, redirecting to home')
    next('/')
  } else {
    console.log('Navigation allowed to:', to.path)
    next()
  }
})

export default router
