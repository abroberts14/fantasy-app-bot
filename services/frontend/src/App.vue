<template>
  <div id="app">
    <NewNavBar v-if="showNavBar " />
    <div v-if="checkToken">
      <OAuthMissingModal  />
    </div>
    <div v-if="userTokenPresent || !checkToken" class="main container">
      <router-view />
    </div>
  </div>
</template>

<script>
import NewNavBar from '@/components/NewNavBar.vue'
import OAuthMissingModal from '@/components/OAuthMissingModal.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute } from 'vue-router';
import useUsersStore from '@/store/users';

export default {
  components: {
    NewNavBar,
    LoadingSpinner,
    OAuthMissingModal
  },
  setup() {
    const usersStore = useUsersStore();
    const route = useRoute();
    const userTokenPresent = ref(false);

    const showNavBar = computed(() => {
      return !(route.meta && route.meta.hideNavBar);
    });

    const checkToken = computed(() => {
      return (route.meta && route.meta.checkToken);
    });
    const inDevelopment = computed(() => {
      return (route.meta && route.meta.development);
    });
    function handleTokenStatus(hasToken) {
      userTokenPresent.value = hasToken;
    }
    
    // Reactively fetch user token when checkToken updates
    watch(() => route.meta, async (newMeta) => {
      if (newMeta.checkToken) {
        await usersStore.viewMe();
        console.log("usersStore.hasOAuthToken", usersStore.hasOAuthToken);
        // Set the dialog visibility based on the presence of a user token
        userTokenPresent.value = usersStore.hasOAuthToken;

      }
    }, { immediate: true });

    onMounted(() => {
      console.log("Component mounted.");
      console.log("checkToken.value: ", checkToken.value);
      console.log("userTokenPresent.value: ", userTokenPresent.value);
    });
    
    // Handle changes in token status received from OAuthMissingModal

    return {
      userTokenPresent,
      handleTokenStatus,
      checkToken,
      inDevelopment,
      showNavBar
    };
  }
}
</script>