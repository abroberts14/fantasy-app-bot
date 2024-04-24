<template>
  <section>
    <form @submit.prevent="submit">
      <div class="mb-3">
        <label for="username" class="form-label">Username:</label>
        <input type="text" name="username" v-model="form.username" class="form-control" />
      </div>
      <div class="mb-3">
        <label for="password" class="form-label">Password:</label>
        <input type="password" name="password" v-model="form.password" class="form-control" />
      </div>
      <button type="submit" class="btn btn-primary">Submit</button>
    </form>
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

