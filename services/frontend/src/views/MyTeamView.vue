<template>

    <p>My Team</p>
  </template>
  
  <script>
  import { ref } from 'vue';
  import useUsersStore from '@/store/users';
  import OauthMissingModal from '@/components/OAuthMissingModal.vue';
  import { onMounted, computed } from 'vue';
  import axios from 'axios';

  export default {
    name: 'MyTeam',
    setup() {
      const usersStore = useUsersStore();
      const user = computed(() => usersStore.user);

      return {
          user
      };
    }
  }
  </script>
  
  <style scoped>
  /* Your component-specific styles go here */
  </style>