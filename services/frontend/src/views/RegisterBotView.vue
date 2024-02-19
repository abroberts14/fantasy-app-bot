<template>
  <section>
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
import { defineComponent } from 'vue';
import useBotsStore from '@/store/bots'; // Import your bots store
import { useToast } from 'vue-toastification';

export default defineComponent({
  name: 'RegisterBotComponent',
  data() {
    return {
      bot: {
        name: '',
        league_id: '',
        groupme_bot_id: '',
      },
    };
  },
  methods: {
    async submit() {
      const toast = useToast();
      const errorMessages = [];
      if (!this.bot.name) {
        errorMessages.push('Bot Name cannot be empty');
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
        const botsStore = useBotsStore(); 
        await botsStore.createBot(this.bot); // Call the action from your bots store

        this.$router.push('/dashboard');
      } catch (error) {
        console.log('Error creating bot');
      }
    },
  },
});
</script>