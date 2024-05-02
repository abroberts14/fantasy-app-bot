<template>
  <div id="app">
    <NewNavBar v-if="showNavBar" />
    <div class="main container">
      
      <router-view />
    </div>
  </div>
</template>

<script>
import NewNavBar from '@/components/NewNavBar.vue'

import LoadingSpinner from '@/components/LoadingSpinner.vue'

export default {
  components: {
    NewNavBar,
    LoadingSpinner,
  },
  computed: {
    showNavBar() {
      return !(this.$route.meta && this.$route.meta.hideNavBar);
    }
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
  padding-top: 5em;
}
</style>
