<template>
  <header>

      <Menubar :model="items" class="">
        <template #start>
          <router-link class="navbar-brand" to="/"><img src="@/assets/dwr_icon.png" alt="Image" height="100" width="100" class="mr-3" />
</router-link>
        </template>
        <template #end v-if="isLoggedIn">
          
          <Button class="p-button-sm no-wrap" severity="secondary" @click="logout">Log Out</Button>
        </template>
      </Menubar>
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
        { label: 'My Profile', to: '/profile', command: () => { router.push('/profile'); } },
        {
          label: 'Chat Bots', // Main menu item for replays
          items: [
             { label: 'My Bots', to: '/dashboard', command: () => { router.push('/dashboard'); } },
            { label: 'Register New Bot', to: '/register-bot', command: () => { router.push('/register-bot'); } },
          ]
        },
        {
          label: 'Video Replays', // Main menu item for replays
          items: [
            { label: 'Search', to: '/pitch-replays', command: () => { router.push('/pitch-replays'); } },
          ]
        },
        { label: 'My Team', to: '/my-team', command: () => { router.push('/my-team'); } },

     
      ];
      if (usersStore.isAdmin) {
        baseItems.push({ label: 'Admin', to: '/admin', command: () => { router.push('/admin'); } });

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
  computed: {
    isLoggedIn() {
      return this.usersStore.isAuthenticated;
    }
  },
  methods: {
    async logout() {
      await this.usersStore.logOut();
      this.$router.push('/login');
    }
  }
})
</script>