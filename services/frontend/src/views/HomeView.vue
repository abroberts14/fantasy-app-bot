<template>
  <section>
    <center>
    <h1 style="font-size: 48px; font-weight: bold; font-family: 'Arial', sans-serif;">Welcome to SRC Bot!</h1> <br>
    <img src="@/assets/srclogo1.png" alt="SRC Bot" 
        width="400" height="400"> <br><br>

    <br>
    <div v-if="isLoggedIn" id="logout">
      <p> Welcome back to SRC Bot!</p>
    </div>
    <h2 v-else>
      <span><a href="/register">Register</a></span>
      <span> or </span>
      <span><a href="/login">Log In</a></span>
    </h2>
    </center>
  </section>
</template>
<script>

import { defineComponent } from 'vue';

export default defineComponent({
  name: 'HomeView',
  computed : {
    isLoggedIn: function() {
      return this.$store.getters.isAuthenticated;
    }
  },
});
</script>
