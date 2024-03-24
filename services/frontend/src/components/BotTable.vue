<template>
  
    <DataTable :value="bots" stripedRows paginator :rows="20" :loading="!loaded" :rowsPerPageOptions="[5, 10, 20, 50]" >
      <Column field="name" header="Bot Name" sortable ></Column>
      <Column field="league_id" header="League ID"></Column>
      <Column header="Platform">
        <template #body="slotProps">
          {{ getPlatformType(slotProps.data) }}
        </template>
      </Column>

      <Column header="Platform ID">
        <template #body="slotProps">
          <span 
            :key="tooltipKey"
            v-tooltip="copiedText === getPlatformId(slotProps.data) ? 'Copied to clipboard!' : getTooltipContent(slotProps.data)"
            @click="copyToClipboard(getPlatformId(slotProps.data), slotProps.data)"
            class="cursor-pointer"
          >
            {{ truncateText(getPlatformId(slotProps.data), 15) }}
          </span>
        </template>
      </Column>
      <Column header="Private">
        <template #body="slotProps">
          <div v-if = "slotProps.data.private">
              Personal
            </div>
            <div v-else >
              Entire Leage
              </div>
        </template>
      </Column>
      <Column field="running" header="Running"> 
          <template #body="slotProps">
            <div v-if = "slotProps.data.app">
              <i class="pi" :class="{ 'pi-check-circle text-green-500': slotProps.data.app.running, 'pi-times-circle text-red-400': !slotProps.data.app.running }"></i>
            </div>
            <div v-else >
              <i class="pi pi-times-circle text-red-400"></i>
              </div>
          </template>
      </Column>

      <Column header="Actions">
        <template #body="slotProps">
          <router-link  class="btn btn-primary btn-sm raised" :to="{name: 'Bot', params:{id: slotProps.data.id}}">View</router-link>
        </template>
      </Column>
    </DataTable>
    <div v-if="bots && !bots.length">
      <p>No fantasy chat bots exist. <router-link to="/register-bot">Register a new bot</router-link></p>
    </div>
  </template>
  

  
<script>
import { defineComponent, ref } from 'vue';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import LoadingSpinner from './LoadingSpinner.vue';
export default defineComponent({
  name: 'BotTable',
  components: {
    DataTable,
    Column,
    LoadingSpinner
  },
  props: {
    bots: {
      type: [Array, null],
      required: true
    },
    loaded: {
      type: Boolean,
      //default: false
    }
  },

  methods: {
    truncateText(text, maxLength) {
      if (!text) {
        return text;
      }
      if (text.length > maxLength) {
        return text.substring(0, maxLength) + '...';
      }
      return text;
    },
    getPlatformType(data) {
      return data.groupme_bot_id ? 'GroupMe' : data.discord_webhook_url ? 'Discord' : '';
    },
    getPlatformId(data) {
      return data.groupme_bot_id || data.discord_webhook_url || '';
    },
    getPlatformId(data) {
      return data.groupme_bot_id || data.discord_webhook_url || '';
    },
    getTooltipContent(data) {
      const fullId = this.getPlatformId(data);
      return fullId ? fullId : 'No ID';
    },
    async copyToClipboard(text) {
      console.log('copying to clipboard', text);
      if (!text) return;
      
      try {
        await navigator.clipboard.writeText(text);
        this.copiedText = text;
        console.log('copied to clipboard', text);
        setTimeout(() => this.copiedText = '', 2000); // Reset after 2 seconds
      } catch (err) {
        console.error('Failed to copy: ', err);
      }
    }
  },
  setup(props) {
    const copiedText = ref('');
    const tooltipKey = ref(0);

    function copyToClipboard(text, data) {
      if (!text) return;
      navigator.clipboard.writeText(text).then(() => {
        copiedText.value = text;
        tooltipKey.value++; // Increment key to force update
        setTimeout(() => copiedText.value = '', 2000); // Reset after 2 seconds
      }).catch(err => {
        console.error('Failed to copy: ', err);
      });
    }

    return { copiedText, tooltipKey, copyToClipboard };
  }
});
</script>

<style>
  .cursor-pointer {
    cursor: pointer;
  }
</style>