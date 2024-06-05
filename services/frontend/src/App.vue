<template>
  <div id="app">
    <NewNavBar v-if="showNavBar " />
    <div v-if="checkToken">
      <OAuthMissingModal @token-status="handleTokenStatus" />
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
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';

export default {
  components: {
    NewNavBar,
    LoadingSpinner,
    OAuthMissingModal
  },
  setup() {
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

    onMounted(() => {
      console.log("check token: ", checkToken.value);
      console.log("token status: ", userTokenPresent.value);
    });

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

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}
.main {
  padding-top: 2em;
}
</style>