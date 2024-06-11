<template>
  <DataTable :value="bots" stripedRows paginator :rows="20" :loading="!loaded ":rowsPerPageOptions="[5, 10, 20, 50]" class="data-table-center">
    <Column field="name" header="Bot Name" sortable class="col-bot-name">
      <template #body="slotProps">
        <Skeleton v-if="!loaded" animation="wave" width="100%" />
        <span v-else>{{ slotProps.data.name }}</span>
      </template>
    </Column>
    <Column field="league_id" header="League ID" class="col-league-id">
      <template #body="slotProps">
        <Skeleton v-if="!loaded" animation="wave" width="100%" />
        <span v-else>{{ slotProps.data.league_id }}</span>
      </template>
    </Column>
    <Column header="Platform" class="col-platform">
      <template #body="slotProps">
        <Skeleton v-if="!loaded" animation="wave" width="100%" />
        <span v-else>{{ getPlatformType(slotProps.data) }}</span>
      </template>
    </Column>
    <Column header="Platform ID" class="col-platform-id">
      <template #body="slotProps">
        <Skeleton v-if="!loaded" animation="wave" width="100%" />
        <span v-else :key="tooltipKey" v-tooltip="copiedText === getPlatformId(slotProps.data) ? 'Copied to clipboard!' : getTooltipContent(slotProps.data)" @click="copyToClipboard(getPlatformId(slotProps.data), slotProps.data)" class="cursor-pointer">
          {{ truncateText(getPlatformId(slotProps.data), 15) }}
        </span>
      </template>
    </Column>
    <Column header="Private" class="col-private">
      <template #body="slotProps">
        <Skeleton v-if="!loaded" animation="wave" width="100%" />
        <div v-else>
          <div v-if="slotProps.data.private">Personal</div>
          <div v-else>Entire League</div>
        </div>
      </template>
    </Column>
    <Column field="running" header="Running" class="col-running">
      <template #body="slotProps">
        <Skeleton v-if="!loaded" animation="wave" width="100%" />
        <div v-else>
          <div v-if="slotProps.data.app">
            <i class="pi" :class="{'pi-check-circle text-green-500': slotProps.data.app.running, 'pi-times-circle text-red-400': !slotProps.data.app.running}"></i>
          </div>
          <div v-else>
            <i class="pi pi-times-circle text-red-400"></i>
          </div>
        </div>
      </template>
    </Column>
    <Column header="Actions" class="col-actions">
      <template #body="slotProps">
        <Skeleton v-if="!loaded" animation="wave" width="100%" />
        <router-link v-else :to="{name: 'Bot', params:{id: slotProps.data.id}}">
          <Button icon="pi pi-pencil" class="p-button-sm" severity="info" label="View"></Button>
        </router-link>
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