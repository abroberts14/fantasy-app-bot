<template>
    <section style="text-align: center; justify-content: center;">

  <div class="login-container">

    <div class="surface-card p-4 shadow-2 border-round w-full lg:w-6">
        <div class="text-center mb-5">
            <img src="@/assets/srclogo1.png" alt="Image" height="50" class="mb-3" />
            <div class="text-900 text-3xl font-medium mb-3">Sign up today!</div>
            <span class="text-600 font-medium line-height-3">Already have an account?</span>
            <router-link to="/" class="font-medium no-underline ml-2 text-blue-500 cursor-pointer">Login instead</router-link>
        </div>

        <div>
            <label for="email1" class="block text-900 font-medium mb-2">Username</label>
            <InputText id="email1" type="text" class="w-full mb-3"  v-model="user.username" invalid />

            <label for="password1" class="block text-900 font-medium mb-2">Password</label>
            <InputText id="password1" type="password" class="w-full mb-3"  v-model="user.password" />

            <label for="full_name" class="block text-900 font-medium mb-2">Full Name</label>
            <InputText id="full_name" type="text" class="w-full mb-3" v-model="user.full_name"  />

            <div class="flex align-items-center justify-content-between mb-6">
            
            </div>

            <Button   @click="submit" label="Register" icon="pi pi-user" class="w-full"></Button>
        </div>
    </div>
  </div>
  </section>
</template>
  

  
<script>
import { defineComponent } from 'vue';
import useUsersStore from '@/store/users'; 
import { useToast } from 'vue-toastification';

export default defineComponent({
  name: 'RegisterComponent',
  data() {
    return {
      user: {
        username: '',
        full_name: '',
        password: '',
      },
    };
  },
  methods: {
    async submit() {

      const toast = useToast();

      const errorMessages = [];
      if (!this.user.username) {
        errorMessages.push('Username cannot be empty');
      }

      if (!this.user.full_name) {
        errorMessages.push('Full name cannot be empty');
      }

      if (!this.user.password) {
        errorMessages.push('Password cannot be empty');
      }

      if (errorMessages.length > 0) {
        toast.error(errorMessages.join(', '));
        return;
      }
      try {
        const usersStore = useUsersStore(); 
        await usersStore.register(this.user); // Call the action from your users store

        this.$router.push('/dashboard');
      } catch (error) {
        throw 'Username already exists. Please try again.';
      }
    },
  },
});
</script>

<style>
  .cursor-pointer {
    cursor: pointer;
  }
  .login-container {
    display: flex;
    justify-content: center;
    align-items: center;
  }
</style>