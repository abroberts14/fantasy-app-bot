<template>
  <header>
    <div class="fixed-menubar">

      <Menubar :model="items" class="">
        <template #start>
          <router-link class="navbar-brand" to="/">SRC Bot</router-link>
        </template>
        <template #end v-if="isLoggedIn">
          <button class="btn btn-secondary btn-sm" @click="logout">Log Out</button>
        </template>
      </Menubar>
    </div>
  </header>
</template>

<script>
import { defineComponent, computed } from 'vue';
import { useRouter } from 'vue-router'; // Import useRouter
import useUsersStore from '@/store/users';

export default defineComponent({
  name: 'NewNavBar',
  setup() {
    const router = useRouter(); // Use useRouter to access the router instance
    const usersStore = useUsersStore();

    const items = computed(() => {
      const baseItems = [
        { label: 'Home', to: '/', command: () => { router.push('/'); } },
        { label: 'Dashboard', to: '/dashboard', command: () => { router.push('/dashboard'); } },
        { label: 'My Profile', to: '/profile', command: () => { router.push('/profile'); } },
        { label: 'Register New Bot', to: '/register-bot', command: () => { router.push('/register-bot'); } }
      ];
      if (usersStore.isAdmin) {
        baseItems.push({ label: 'Admin', to: '/admin', command: () => { router.push('/admin'); } });
        baseItems.push({ label: 'Pitch Replays', to: '/pitch-replays', command: () => { router.push('/pitch-replays'); } });
      }
      if (!usersStore.isAuthenticated) {
        baseItems.push({ label: 'Log In', to: '/login', command: () => { router.push('/login'); } });
        baseItems.push({ label: 'Register', to: '/register', className: 'btn btn-primary btn-sm', command: () => { router.push('/register'); } });
      }
      return baseItems;
    });

    return {
      usersStore,
      items
    };
  },
  methods: {
    async logout() {
      await this.usersStore.logOut();
      router.push('/');
    }
  }
})
</script>