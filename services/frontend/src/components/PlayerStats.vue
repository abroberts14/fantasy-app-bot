<template>
    <div>
      <h1>Player Statistics</h1>

      <DataTable v-if="currentPlayer" :value="[currentPlayer]" showGridlines removableSort class="compact-table" stripedRows scrollable>
        <Column field="name" header="Name" class="compact-column" frozen>
          <template #body="slotProps">
            <div class="name-image-container">
              <img :src="`https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_213,q_auto:best/v1/people/${slotProps.data.key_mlbam}/headshot/67/current`" :alt="slotProps.data.name" class="img-headshot" />
              <span>{{ slotProps.data.name }}</span>
            </div>
          </template>
        </Column>
        <Column v-for="field in fields.custom" sortable   :field="`stats.${activeStatPeriod}.` + field.key" :header="field.label" class="compact-column right-aligned">
            <template #body="slotProps">
              <Skeleton v-if="isLoading" animation="wave" width="2rem" class="mb-2"/>
              <span v-else>{{ slotProps.data.stats?.[activeStatPeriod]?.[field.key] }}</span>
            </template>
        </Column>
      </DataTable>
   
    </div>  
  </template>
  
  




  <script>
    import { ref, onMounted, computed } from 'vue';
    import axios from 'axios';
    import { useRoute } from 'vue-router';
    import usePlayersStore from '@/store/players';
    export default {
        name: 'PlayerStats',
    
        setup() {
            
            const playersStore = usePlayersStore();
            const activeStatPeriod = ref('all');  // Default to all time stats
            const currentPlayer = computed(() => playersStore.statePlayer);
            const isLoading = computed(() => playersStore.stateIsPlayerLoading);

            const fields = playersStore.getPlayerFields();

            onMounted(async () => {
                const route = useRoute();
                const playerId = route.params.id;  // Extract player ID from the URL path
                if (playerId) {
                    await playersStore.fetchPlayerStats(playerId);
                    console.log(currentPlayer.value);
                }
            });
           return {
            currentPlayer,
            activeStatPeriod,
            fields,
            isLoading
           }

                
        }
    }

  </script>
