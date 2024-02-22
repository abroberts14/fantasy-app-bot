<template>
  <section>
    <LoadingSpinner v-if="isLoading" />
    <form @submit.prevent="submit">
      <div class="mb-3">
        <label for="bot_name" class="form-label">Bot Name:</label>
        <input type="text" name="bot_name" v-model="bot.name" class="form-control" />
      </div>
      <div class="mb-3">
        <label for="league_id" class="form-label">Yahoo League ID:</label>
        <input type="text" name="league_id" v-model="bot.league_id" class="form-control" />
      </div>
      <div class="mb-3">
        <label for="groupme_bot_id" class="form-label">GroupMe Bot ID:</label>
        <input type="text" name="groupme_bot_id" v-model="bot.groupme_bot_id" class="form-control" />
      </div>
      <button type="submit" class="btn btn-primary">Submit</button>
    </form>
 
  </section>
</template>

<script>
import { defineComponent, ref } from 'vue';
import useBotsStore from '@/store/bots'; // Import your bots store
import { useToast } from 'vue-toastification';
import LoadingSpinner from '@/components/LoadingSpinner.vue';
export default defineComponent({
  name: 'RegisterBotComponent',
  data() {
    return {
      bot: {
        name: '',
        league_id: '',
        groupme_bot_id: '',
      },
      isLoading : false
    };
  },
  components: { LoadingSpinner },


  methods: {
    async submit() {
      const toast = useToast();
      const errorMessages = [];
      const namePattern = /^[A-Za-z0-9]+$/; // Regex for letters and digits

      if (!this.bot.name) {
        errorMessages.push('Bot Name cannot be empty');
      } else if (!namePattern.test(this.bot.name)) {
        errorMessages.push('Bot Name should contain only letters and numbers,no spaces or special characters');
      }
      if (this.bot.name.length > 20) {
        errorMessages.push('Bot Name must be 10 characters or less');
      }
      if (!this.bot.league_id) {
        errorMessages.push('Yahoo League ID cannot be empty');
      }

      if (!this.bot.groupme_bot_id) {
        errorMessages.push('GroupMe Bot ID cannot be empty');
      }

      if (errorMessages.length > 0) {
        for (const errorMessage of errorMessages) {
          toast.error(errorMessage);
        }
        return;
      }

      try {
        this.isLoading = true;
        const botsStore = useBotsStore(); 
        await botsStore.createBot(this.bot); // Call the action from your bots store
        toast.success('Bot created successfully');
        this.$router.push('/dashboard');
        this.isLoading = false;

      } catch (error) {
        console.log('Error creating bot');
        toast.error('Error creating bot: ' + error);
      }
    },
  },
});
</script>