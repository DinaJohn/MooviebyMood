import { createRouter, createWebHistory } from 'vue-router'
import ScoreTag from '../pages/Score-Tag.vue';
import Tag from '../pages/Tag.vue';
import LoginPage from '../pages/LoginPage.vue';
import Logout from '../pages/Logout.vue';
import Logo from '../pages/Logo.vue';
import About from '../pages/About.vue';
import { useAuthStore } from '../store/User_auth';

let base = (import.meta.env.MODE == 'development') ? import.meta.env.BASE_URL : '';

const routes = [
    { path: '/', name: 'Logo', component: Logo },
    { path: '/scoretag', name: 'Score-Tag based Recommendations', component: ScoreTag },
    { path: '/tag', name: 'Tag-based Recommendations', component: Tag },
    { path: '/login', name: 'Login', component: LoginPage },
    { path: '/logout', name: 'Logout', component: Logout, meta: { requiresAuth: true } },
    { path: '/about', name: 'About', component: About },
];

const router = createRouter({
    history: createWebHistory(base),
    routes,
});

router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore();
  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    next({ name: 'Login' });
  } else {
    next();
  }
});

export default router;
