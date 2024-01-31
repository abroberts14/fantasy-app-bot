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
import { mapActions } from 'vuex';

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
    ...mapActions(['createBot']),
    async submit() {
    try {
      await this.createBot(this.bot);
      this.$router.push('/dashboard');
    } catch (error) {
      console.error(new Error('Bot name already exists. Please try again.'));
    }
  },
  },
});
</script>

