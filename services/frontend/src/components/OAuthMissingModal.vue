<template>
    <ModalOverlay :isVisible="isDialogVisible" @update:isVisible="handleModalVisibilityChange">
      <h3>No Yahoo Account Detected</h3>
      <p>
        To search for your players most recent plate appearances, you must connect and authorize a Yahoo account.
      </p>
      <p>
        Visit your <router-link to="/profile">profile</router-link> for Yahoo integration setup.
      </p>
  </ModalOverlay> 
  <Message v-if="!isDialogVisible" severity="info" :sticky="false" :life="5000">Resync your players on your <router-link to="/profile">profile</router-link> page</Message>

  </template>
  
  <script>
  import { ref } from 'vue';
  import ModalOverlay from '@/components/ModalOverlay.vue';
  import { onMounted, computed } from 'vue';
  import axios from 'axios';
  import useUsersStore from '@/store/users';
  import { useRouter } from 'vue-router';
  export default {
    name: 'OauthMissingModal',
    components: {
      ModalOverlay,
    },
    emits: ['token-status'],

    setup(props, { emit }) {  // Include emit here
      const isDialogVisible = ref(false);
      const userTokenPresent = ref(null);
      const usersStore = useUsersStore();
      const user = computed(() => usersStore.user);
      const router = useRouter();

      const handleModalVisibilityChange = (newValue) => {
        isDialogVisible.value = newValue;
        if (!newValue) { // if newValue is false, indicating the modal is closed
          router.push('/profile'); // navigate to /profile
        }

      };
      onMounted(fetchUserTokens);
      async function fetchUserTokens() {
        try {
          const response = await axios.get(`/oauth/yahoo/tokens`, {
            params: {
              user_id: user.value.id
            }
          });        
          console.log('API Response:', response.data);
          userTokenPresent.value = response.data;
          isDialogVisible.value = !userTokenPresent.value 
          emit('token-status', userTokenPresent.value); // Emit the token presence status

        } catch (error) {
          console.error('Failed to fetch Yahoo integration:', error);
          isDialogVisible.value = true;
          userTokenPresent.value = false;
          emit('token-status', userTokenPresent.value); // Emit the token presence status

        }
        finally {

          console.log("isDialogVisible: ", isDialogVisible.value);
        }
      }
      return {
        isDialogVisible,
        handleModalVisibilityChange,
        fetchUserTokens
      };
    }
  }
  </script>
  
  <style scoped>
  /* Your component-specific styles go here */
  </style>