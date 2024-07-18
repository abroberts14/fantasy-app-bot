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
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import ModalOverlay from '@/components/ModalOverlay.vue';
import useUsersStore from '@/store/users'; 

export default {
  components: {
    ModalOverlay
  },
  setup() {
    const isDialogVisible = ref(false);
    const router = useRouter();
    const usersStore = useUsersStore(); 

    // Function to handle modal visibility changes
    const handleModalVisibilityChange = (isVisible) => {
      isDialogVisible.value = isVisible;
      if (!isVisible) { // if newValue is false, indicating the modal is closed
        router.push('/profile'); // navigate to /profile
      }
    };

    onMounted(async () => {
      await usersStore.viewMe();
      console.log("usersStore.hasOAuthToken", usersStore.hasOAuthToken);
      // Set the dialog visibility based on the presence of a user token
      isDialogVisible.value = !usersStore.hasOAuthToken;
    });

    return { isDialogVisible, handleModalVisibilityChange };
  }
}
</script>


