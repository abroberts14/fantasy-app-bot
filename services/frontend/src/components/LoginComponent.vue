<template>
    <section style="text-align: center; justify-content: center;">

  <div class="login-container">

    <div class="surface-card p-4 shadow-2 border-round w-full lg:w-6">
        <div class="text-center mb-5">
            <img src="@/assets/srclogo1.png" alt="Image" height="50" class="mb-3" />
            <div class="text-900 text-3xl font-medium mb-3">Welcome!</div>
            <span class="text-600 font-medium line-height-3">Don't have an account?</span>
            <router-link  to="/register" class="font-medium no-underline ml-2 text-blue-500 cursor-pointer">Create today!</router-link>
        </div>

        <div>
            <label for="email1" class="block text-900 font-medium mb-2">Username</label>
            <InputText id="email1" type="text" class="w-full mb-3" v-model="form.username"/>

            <label for="password1" class="block text-900 font-medium mb-2">Password</label>
            <InputText id="password1" type="password" class="w-full mb-3" v-model="form.password"  />

            <div class="flex align-items-center justify-content-between mb-6">
            
            </div>

            <Button   @click="submit" label="Sign In" icon="pi pi-user" class="w-full"></Button>
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
  name: 'LoginComponent',
  data() {
    return {
      form: {
        username: '',
        password: '',
      },
    };
  },
  methods: {
    async submit() {
      console.log("Forms: ", this.form);
      try {
        const toast = useToast();

        const errorMessages = [];
        if (!this.form.username) {
          errorMessages.push('Username cannot be empty');
        }

        if (!this.form.password) {
          errorMessages.push('Password cannot be empty');
        }

        if (errorMessages.length > 0) {
          toast.error(errorMessages.join(', '));
          return;
        }

        const User = new FormData();
        User.append('username', this.form.username);
        User.append('password', this.form.password);

        const usersStore = useUsersStore(); 
        await usersStore.logIn(User); // Call the action from your users store

        this.$router.push('/dashboard');
      } catch (error) {
        console.log("Login Failed: ", error);

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