<template>
  <div v-if="bot && (isAdmin || userOwnsBot)" >

    <div class="surface-section">
        <div class="font-medium text-3xl text-900 mb-3">{{ bot.name }}</div>
        <div class="text-500 mb-5">Created: {{ bot.created_at }}</div>
        <ul class="list-none p-0 m-0">
            <li class="flex align-items-center py-3 px-2 border-top-1 surface-border flex-wrap">
                <div class="text-500 w-6 md:w-2 font-medium">Name</div>
                <div class="text-900 w-full md:w-8 md:flex-order-0 flex-order-1">{{ bot.name }}</div>
           
            </li>

            <li class="flex align-items-center py-3 px-2 border-top-1 surface-border flex-wrap">
                <div class="text-500 w-6 md:w-2 font-medium"> Status
                </div>
                <div class="text-900 w-full md:w-8 md:flex-order-0 flex-order-1">
                    <Button v-if="bot.running" label="Running" severity="success" />
                    <Button v-else label="Stopped" severity="danger"     />
           
                </div>
            </li>
            <li class="flex align-items-center py-3 px-2 border-top-1 surface-border flex-wrap">
                <div class="text-500 w-6 md:w-2 font-medium">League ID</div>
                <div class="text-900 w-full md:w-8 md:flex-order-0 flex-order-1">{{bot.league_id}}</div>
            </li>
            <li class="flex align-items-center py-3 px-2 border-top-1 border-bottom-1 surface-border flex-wrap">
                <div class="text-500 w-6 md:w-2 font-medium">GroupMe Bot ID</div>
                <div class="text-900 w-full md:w-8 md:flex-order-0 flex-order-1 line-height-3">
                  {{bot.groupme_bot_id}}
                </div>
            </li>
        </ul>
    </div>
    <!-- <p><strong>Bot Name:</strong> {{ bot.name }}</p>
    <p><strong>League ID:</strong> {{ bot.league_id }}</p>
    <p><strong>GroupMe Bot ID:</strong> {{ bot.groupme_bot_id }}</p> -->
  
    <p><router-link :to="{name: 'EditBot', params:{id: bot.id}}" class="btn btn-primary">Edit</router-link></p>
    <p>
        <Button label="Delete" class="p-button-secondary" @click="removeBot()" />
    </p>

  </div>  
</template>
<script>
import { defineComponent, onMounted, computed, ref} from 'vue';
import useBotsStore from '@/store/bots'; 
import useUsersStore from '@/store/users'; 

export default defineComponent({
  name: 'BotComponent',
  props: ['id'],
  setup(props) {
    const botsStore = useBotsStore();
    const usersStore = useUsersStore();

    onMounted(async () => {
      console.log("Fetching data"); // Debugging line
      await botsStore.viewBot(props.id); 
      await usersStore.viewMe();
    });

    const bot = computed(() => botsStore.stateBot);
    const user = computed(() => usersStore.stateUser);
    const isAdmin = computed(() => usersStore.isAdmin);
    const userOwnsBot = computed(() => user.value.id === bot.user.id);
    console.log("user id: ", user.value.id); // Debugging line
    //console.log("bot user id: ", bot.value.user.id); // Debugging line
    console.log("Bot: ", bot); // Debugging line
    console.log("User: ", user); // Debugging line
    console.log("isAdmin: ", isAdmin); // Debugging line
    console.log("userOwnsBot: ", userOwnsBot); // Debugging line
    const removeBot = async () => {
      if (bot) {
        await botsStore.deleteBot(props.id);
      }      
    };
    
    return { bot, user, isAdmin, userOwnsBot, removeBot };
  }
});
</script>