<template>
  <section>
    <h1>Edit Bot</h1>
    <hr/><br/>

    <form @submit.prevent="submit">
      <div class="mb-3">
        <label for="name" class="form-label">Name:</label>
        <input type="text" name="name" v-model="form.name" class="form-control" />
      </div>
      <div class="mb-3">
        <label for="groupme_bot_id" class="form-label">GroupMe Bot ID:</label>
        <input type="text" name="groupme_bot_id" v-model="form.groupme_bot_id" class="form-control" />
      </div>
      <button type="submit" class="btn btn-primary">Submit</button>
    </form>
  </section>
</template>

<script>
import { defineComponent } from 'vue';
import useBotsStore from '@/store/bots'; 

export default defineComponent({
  name: 'EditBot',
  props: ['id'],
  data() {
    return {
      form: {
        name: '',
        groupme_bot_id: '',
      },
    };
  },
  created() {
    this.getBot();
  },
  computed: {
    bot() {
      const botsStore = useBotsStore(); 
      return botsStore.stateBot; 
    },
  },
  methods: {
    async submit() {
      try {
        let bot = {
          id: this.id,
          form: this.form,
        };
        const botsStore = useBotsStore(); 
        await botsStore.updateBot(bot); 
        this.$router.push({name: 'Bot', params:{id: this.bot.id}});
      } catch (error) {
        console.log(error);
      }
    },
    async getBot() {
      try {
        const botsStore = useBotsStore(); 
        await botsStore.viewBot(this.id); 
      } catch (error) {
        console.log(error);
      }
    },
  },
});
</script>