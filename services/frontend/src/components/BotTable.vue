<template>
    <div>
  
      <DataTable v-if="bots" :value="bots" stripedRows paginator :rows="20" :rowsPerPageOptions="[5, 10, 20, 50]" >
        <Column field="name" header="Bot Name" sortable ></Column>
        <Column field="league_id" header="League ID"></Column>
        <Column field="groupme_bot_id" header="GroupMe Bot ID"></Column>
        <Column field="running" header="Running">
            <template #body="slotProps">
                <i class="pi" :class="{ 'pi-check-circle text-green-500': slotProps.data.running, 'pi-times-circle text-red-400': !slotProps.data.running }"></i>
            </template>
        </Column>

        <Column header="Actions">
          <template #body="slotProps">
            <router-link :to="{name: 'Bot', params:{id: slotProps.data.id}}">View</router-link>
          </template>
        </Column>
      </DataTable>
  
      <div v-else>
        <p>No fantasy chat bots exist. <router-link to="/register-bot">Register a new bot</router-link></p>
      </div>
    </div>
  </template>
  
  <script>
  import { defineComponent } from 'vue';
  import DataTable from 'primevue/datatable';
  import Column from 'primevue/column';
  
  export default defineComponent({
    name: 'BotTable',
    components: {
      DataTable,
      Column
    },
    props: {
      bots: {
        type: Array,
        required: true
      }
    }
  });
  </script>
  