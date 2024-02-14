<template>
  <section>
    <h1>Your Profile</h1>
    <hr/><br/>
    <div>
      <p><strong>Full Name:</strong> <span>{{ user.full_name }}</span></p>
      <p><strong>Username:</strong> <span>{{ user.username }}</span></p>
      <p><button @click="deleteAccount()" class="btn btn-primary">Delete Account</button></p>
    </div>
  </section>
</template>

<script>
import { defineComponent } from 'vue';
import useUsersStore from '@/store/users'; 

export default defineComponent({
  name: 'ProfileComponent',
  async created() {
    const usersStore = useUsersStore(); 
    await usersStore.viewMe(); // Call the action from your users store
  },
  computed: {
    user() {
      const usersStore = useUsersStore(); 
      return usersStore.stateUser; 
    },
  },
  methods: {
    async deleteAccount() {
      try {
        const usersStore = useUsersStore(); 
        await usersStore.deleteUser(this.user.id); // Call the action from your users store
        await usersStore.logOut(); // Call the action from your users store
        this.$router.push('/');
      } catch (error) {
        console.error(error);
      }
    },
  },
});
</script>