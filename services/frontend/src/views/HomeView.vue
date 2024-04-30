<!-- <template>
  <section style="text-align: center;">
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
   
   

  </section>
</template> -->


<template>
  <section style="text-align: center; justify-content: center;">

      <div v-if="isLoggedIn" id="logout">
        <p> Welcome back to DWR Bot!</p>
      </div>
      <div v-else>
        <div class="p-d-flex p-jc-center p-ai-center" style="height: 100vh;">

           <LoginComponent />
      </div>
   
</div>
  </section>
</template>

<script>
import { defineComponent, onMounted } from 'vue';
import useUsersStore from '@/store/users'; 
import LoginComponent from '@/components/LoginComponent.vue'; 

export default defineComponent({
  name: 'HomeView',

  components: {
    LoginComponent,
  },
  computed: {
    isLoggedIn() {
      const usersStore = useUsersStore(); 
      return usersStore.isAuthenticated; 
    },
  },
  mounted() {
    if (this.isLoggedIn) {
      this.$router.push('/dashboard');
    }
  },
});
</script>