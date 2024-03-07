<template>
    <DataTable :value="bots" stripedRows paginator :rows="20" :loading="!loaded" :rowsPerPageOptions="[5, 10, 20, 50]" >
      <Column field="name" header="Bot Name" sortable ></Column>
      <Column field="league_id" header="League ID"></Column>
      <Column field="groupme_bot_id" header="GroupMe Bot ID"></Column>
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
  import { defineComponent } from 'vue';
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
  }
});
</script>
  