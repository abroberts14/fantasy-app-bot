import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import RegisterView from '@/views/RegisterView.vue'
import RegisterBotView from '@/views/RegisterBotView.vue'
import LoginView from '@/views/LoginView.vue'
import DashboardView from '@/views/DashboardView.vue'
import ProfileView from '@/views/ProfileView.vue'
import BotView from '@/views/BotView.vue'
import EditBotView from '@/views/EditBotView.vue'
import AdminView from '@/views/AdminView.vue'
import useUsersStore from '@/store/users'; 
import OAuthSuccessView from '@/views/OAuthSuccessView.vue'
import OAuthErrorView from '@/views/OAuthErrorView.vue'
import PitchReplaysView from '@/views/PitchReplaysView.vue'
import TeamVideosView from '@/views/TeamVideosView.vue'
import TeamPercentilesView from '@/views/TeamPercentilesView.vue'
import TeamStatsView from '@/views/TeamStatsView.vue'
import MyTeamView from '@/views/MyTeamView.vue'
import MyTeamViewNew from '@/views/MyTeamViewNew.vue'
import ComparisonView from '@/views/ComparisonView.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomeView,
    meta: { hideNavBar: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: RegisterView,
    meta: { hideNavBar: true }

  },
  {
    path: '/register-bot',
    name: 'RegisterBot',
    component: RegisterBotView,
    meta: { checkToken: true },

  },
  {
    path: '/login',
    name: 'Login',
    component: HomeView,
    meta: { hideNavBar: true }

  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: DashboardView,
    meta: { requiresAuth: true }
  },
  {
    path: '/admin',
    name: 'Admin',
    component: AdminView,
    meta: { requiresAuth: true, requiresAdmin: true}
  },
  {
    path: '/profile',
    name: 'Profile',
    component: ProfileView,
    meta: { requiresAuth: true }
  },
  {
    path: '/bot/:id',
    name: 'Bot',
    component: BotView,
    meta: { requiresAuth: true },
    props: true
  },
  {
    path: '/bot/:id',
    name: 'EditBot',
    component: EditBotView,
    meta: { requiresAuth: true },
    props: true
  },
  {
    path: '/oauth-success',
    name: 'OAuthSuccess',
    component: OAuthSuccessView
  },
  {
    path: '/oauth-error',
    name: 'OAuthError',
    component: OAuthErrorView
  },
  {
    path: '/pitch-replays',
    name: 'PitchReplays',
    component: PitchReplaysView,
  },
  {
    path: '/comparison',
    name: 'Comparison',
    component: ComparisonView,
  },
  {
    path: '/team-videos',
    name: 'TeamVideos',
    meta: { checkToken: true },
    component: TeamVideosView,
  },
  {
    path: '/team-percentiles',
    name: 'TeamPercentiles',
    meta: { checkToken: true },
    component: TeamPercentilesView,
  },
  {
    path: '/team-stats',
    name: 'TeamStats',
    meta: { checkToken: true , development: true},
    component: TeamStatsView,
  },
  {
    path: '/my-team',
    name: 'MyTeam',
    meta: { checkToken: true, development: true },
    component: MyTeamView,
  },
  {
    path: '/my-team-new',
    name: 'MyTeamNew',
    meta: { checkToken: true, development: true },
    component: MyTeamViewNew,
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

router.beforeEach((to, _, next) => {
  if (to.matched.some((record) => record.meta.requiresAuth)) {
    const userStore = useUsersStore(); 
    if (userStore.isAuthenticated) {
      if (to.matched.some((record) => record.meta.requiresAdmin)) {
        if (userStore.isAdmin) {
          next()
          return
        }
        next('/dashboard')
        return
      }
      next()
      return
    }
    next('/login')
  } else {
    next()
  }
})

export default router
