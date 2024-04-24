<template>
  <!-- <section>
    <form @submit.prevent="submit">
      <div class="mb-3">
        <label for="username" class="form-label">Username:</label>
        <input type="text" name="username" v-model="user.username" class="form-control" />
      </div>
      <div class="mb-3">
        <label for="full_name" class="form-label">Full Name:</label>
        <input type="text" name="full_name" v-model="user.full_name" class="form-control" />
      </div>
      <div class="mb-3">
        <label for="password" class="form-label">Password:</label>
        <input type="password" name="password" v-model="user.password" class="form-control" />
      </div>
      <button type="submit" class="btn btn-primary">Submit</button>
    </form>
  </section> -->
  <RegisterComponent />
</template>

<script>
import { defineComponent } from 'vue';
import useUsersStore from '@/store/users'; 
import { useToast } from 'vue-toastification';
import RegisterComponent from '@/components/RegisterComponent.vue'; 

export default defineComponent({
  name: 'RegisterView',

  components: {
    RegisterComponent,
  },
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