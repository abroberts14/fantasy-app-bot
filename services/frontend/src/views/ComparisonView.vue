<template>
  <div class="w-full">
    <div class="flex align-items-start justify-content-between  ">
      <div class="flex align-items-center justify-content-start flex-wrap  w-6 mr-1">
        <div class="flex justify-center w-full">
          <!-- <OrderList v-model="selectedPlayersChips" dataKey="id" breakpoint="250px" scrollHeight="20rem" >
              <template #option="{ option , selected }">
                <div class="flex flex-wrap p-1 items-center gap-1 w-full">
                  <div class="name-image-container">
                    <img  class="img-headshot"  :src="`https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_213,q_auto:best/v1/people/${option.id}/headshot/67/current`" :alt="option.name" />
                  </div>
                      <div class="flex-1 flex flex-col">
                          <span class="font-medium text-sm">{{ option.name }}</span>
                      </div>
                  
                  </div>
              </template>
          </OrderList> -->
          <VirtualScroller :items="computedSelectedPlayersChips" :emit-update="true" :itemSize=60 class="w-full  border-top-1 border-round-sm"  style="height: 10rem; border-color: rgba(0, 0, 0, 0.1);" >
            <template v-slot:item="{ item, options }">
              <div :class="['flex items-center  p-1 gap-1 w-full', { 'bg-surface-100 dark:bg-surface-700': options.odd }]">
                <!-- <div class="name-image-container">
                  <img class="img-headshot" :src="`https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_213,q_auto:best/v1/people/${item.key_mlbam}/headshot/67/current`" :alt="item.name" />
                </div> -->

                  <Chip class="font-medium text-sm w-full sm:w-10rem md:w-10rem lg:w-10rem xl:w-10rem"  removable @remove="removePlayerChip(item)">
                    <span >
                      <img class=" border-circle w-2rem h-3rem flex align-items-center justify-content-center" :src="`https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_213,q_auto:best/v1/people/${item.key_mlbam}/headshot/67/current`" :alt="item.name" />
                    </span>
                    <span class="ml-2 font-medium">{{ item.name }}</span>

                    
                  </Chip>
              </div>
            </template>
          </VirtualScroller>
        </div>
        
      </div>

      <div class="flex flex-wrap justify-content-start  w-6 ml-1">
          
          <SearchPlayers @playerSelected="handlePlayerChipsUpdate" :disabled="loadingData" />
          <Select v-model="selectedDate" inputId="daterange" :options="dates" :disabled="loadingData" optionLabel="name" placeholder="Dates" class="w-full mt-2"/>


          <div class="flex flex-wrap align-items-center justify-content-start w-full ">
            <ToggleSwitch v-model="rankings" :binary="true" inputId="rankings" name="rankings" :disabled="loadingData" />
            <label for="rankings" class="m-1"
              :class="{ 'disabled-label': loadingData }">Percentile Rankings</label>
          </div>
            <Button @click="fetchStatsAllPlayers" class="mt-2" :disabled="loadingData">Compare</Button>
      </div>
      
    </div>

    <Divider type="solid" class="mt-2"/>


    <DataTable v-show="filteredData.length > 0 && !rankings" :value="filteredData" showGridlines removableSort class="compact-table" stripedRows scrollable>
        <Column field="name" header="Name" class="compact-column" frozen>
          <template #body="slotProps">
            <div class="name-image-container">
              <img :src="`https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_213,q_auto:best/v1/people/${slotProps.data.key_mlbam}/headshot/67/current`" :alt="slotProps.data.name" class="img-headshot" />
              <span>{{ slotProps.data.name }}</span>
            </div>
          </template>
        </Column>
        <Column v-for="field in fields.custom" sortable  :key="field.key" :field="`stats.${activeStatPeriod}.` + field.key" :header="field.label" class="compact-column right-aligned">
          <template #body="slotProps">

            <Skeleton v-if="loadingData" animation="wave" width="2rem" class="mb-2"/>
            <div v-else>
              <div v-if="getStatModel(slotProps, field.key) !== '' && getStatModel(slotProps, field.key) !== null && getStatModel(slotProps, field.key) !== undefined">                
                <span>{{ getStatModel(slotProps, field.key) }}</span>
              </div>
            </div>
           
          </template>
        </Column>
      </DataTable>
      <DataTable v-show="filteredData.length > 0 && rankings " :value="filteredData" showGridlines  removableSort  class="compact-table" stripedRows scrollable>
        <Column field="name" header="Name" class="compact-column" frozen>
          <template #body="slotProps">
            <div class="name-image-container">
              <img :src="`https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_213,q_auto:best/v1/people/${slotProps.data.key_mlbam}/headshot/67/current`" :alt="slotProps.data.name" class="img-headshot" />
              <span>{{ slotProps.data.name }}</span>
            </div>
          </template>
        </Column>
        <Column v-for="field in fields.percentiles" sortable   :key="field.key" :field="`stats.${activeStatPeriod}.` + field.key" :header="field.label" class="compact-column right-aligned">
          <template #body="slotProps">

            <Skeleton v-if="loadingData" animation="wave" width="2rem" class="mb-2"/>
            <div v-else>
              <div v-if="getStatModel(slotProps, field.key) !== '' && getStatModel(slotProps, field.key) !== null && getStatModel(slotProps, field.key) !== undefined">                
                <!-- <Knob v-if="rankings" v-model="slotProps.data.stats[activeStatPeriod][field.key]" readonly :min="0" :max="100" :size="100" ></Knob> -->
                <ColorfulBadge v-if="rankings" :value="slotProps.data.stats[activeStatPeriod][field.key]"></ColorfulBadge>

              </div>
            </div>
           
          </template>
        </Column>
      </DataTable>
  </div>

</template>

<script>
import useUsersStore from '@/store/users'
import { defineComponent, ref, computed, watch } from 'vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import axios from 'axios'
import SearchPlayers from '@/components/SearchPlayers.vue'
import ColorfulBadge from '@/components/ColorfulBadge.vue'

export default defineComponent({
  name: 'ComparisonView',
  components: {
    LoadingSpinner,
    SearchPlayers,
    ColorfulBadge
  },
  setup() {
    const usersStore = useUsersStore()
    const advanced = ref(false)
    const rankings = ref(false)
    const selectedDate = ref(null)
    const loadingData = ref(false)
    const isPageLoading = ref(false)
    const dates = ref([
      { name: 'Season', code: 'all' },
      { name: '7 Day', code: 'days7' },
      { name: '14 Day', code: 'days14' },
      { name: '30 Day', code: 'days30' }
    ])
    const activeStatPeriod = ref('all');  // Default to all time stats

    const fields = ref({
      basic: [

        { key: 'G', label: 'G' },
        { key: 'AB', label: 'AB' },
        { key: 'PA', label: 'PA' },
        { key: 'H', label: 'H' },
        { key: 'HR', label: 'HR' },
        { key: 'R', label: 'R' },
        { key: 'RBI', label: 'RBI' },
        { key: 'AVG', label: 'AVG' },
        { key: 'OBP', label: 'OBP' },
        { key: 'SLG', label: 'SLG' },
        { key: 'OPS', label: 'OPS' },
      ],
      custom: [
        { key: 'BABIP', label: 'BABIP' },
        { key: 'BB%', label: 'BB%' },
        { key: 'K%', label: 'K%' },
        { key: 'SwStr%', label: 'SwStr%' },
        { key: 'wOBA', label: 'wOBA' },
        { key: 'ISO', label: 'ISO' },
        { key: 'HR/FB', label: 'HR/FB' },
        { key: 'FB%', label: 'FB%' },
        { key: 'GB%', label: 'GB%' },
        { key: 'LD%', label: 'LD%' },
        { key: 'Soft%', label: 'Soft%' },
        { key: 'Med%', label: 'Med%' },
        { key: 'Hard%', label: 'Hard%' },
        { key: 'Barrels', label: 'Barrels' },
        { key: 'Barrel%', label: 'Barrel%' },
        { key: 'maxEV', label: 'maxEV' },
        { key: 'HardHit%', label: 'HardHit%' },
        { key: 'xBA', label: 'xBA' },
        { key: 'xSLG', label: 'xSLG' },
        { key: 'xwOBA', label: 'xwOBA' },
        { key: 'wRC+', label: 'wRC+' },
        { key: 'O-Swing%', label: 'O-Swing%' },
        { key: 'Z-Swing%', label: 'Z-Swing%' },
        { key: 'O-Contact%', label: 'O-Contact%' },
        { key: 'Z-Contact%', label: 'Z-Contact%' },
        { key: 'CSW%', label: 'CSW%' }
      ], 
      percentiles: [
        { key: 'K%', label: 'K%' },
        { key: 'BB%', label: 'BB%' },
        { key: 'xBA', label: 'xBA' },
        { key: 'xSLG', label: 'xSLG' },
        { key: 'wOBA', label: 'wOBA' },
        { key: 'xwOBA', label: 'xWOBA' },
        { key: 'EV', label: 'EV' },
        { key: 'Barrel%', label: 'Barrel%' },
        { key: 'HardHit%', label: 'HardHit%' },
        { key: 'O-Swing%', label: 'O-Swing%' },
        { key: 'SwStr%', label: 'SwStr%' },
        { key: 'CSW%', label: 'CSW%' },
        { key: 'wRC+', label: 'wRC+' }
      ]
    });

    const getStatModel = (slotProps, key) => {

      const periodStats = slotProps.data.stats[activeStatPeriod.value];
      if (!periodStats) {
        slotProps.data.stats[activeStatPeriod.value] = {};
      }
      return periodStats[key] !== undefined ? periodStats[key] : null;

    };

    const filteredData = computed(() => {
      return batters.value.map(player => ({
        ...player,
        stats: player.stats? player.stats : {}
      }));
    });

    const selectedPlayersChips = ref([])
    const computedSelectedPlayersChips = computed(() => {
      return selectedPlayersChips.value.map(player => ({
        name: player.name,
        name_first: player.name_first,
        name_last: player.name_last,
        key_mlbam: player.key_mlbam
      }))
    })
    const batters = ref([])
    const setStatPeriod = (period) => {
      activeStatPeriod.value = period;
    };

    watch(rankings, (newRankings, oldRankings) => {
        if (newRankings) {
          setStatPeriod(`${activeStatPeriod.value}_ranks`);
        } else {
          setStatPeriod('all');
        }
      
        console.log(activeStatPeriod.value);
        console.log(batters.value)
    });
    // Watch for changes in selectedPlayersChips and log them
    watch(selectedPlayersChips, (newVal) => {
      console.log('selectedPlayersChips updated:', newVal);
    });
    // Watch for changes in selectedDate
    watch(selectedDate, (newDate, oldDate) => {
        if (newDate) {
          if (rankings.value) {
            setStatPeriod(`${newDate.code}_ranks`);
          } else {
            setStatPeriod(newDate.code);
          }
        }
    });
    async function fetchStatsAllPlayers() {
      loadingData.value = true;
      // set batters to the computedchips
      console.log('selectedcomputedPlayersChips:', computedSelectedPlayersChips.value);

      batters.value = computedSelectedPlayersChips.value.map(player => ({ ...player }));

      const playerIds = batters.value.map(player => player.key_mlbam);
      console.log('batters:', batters.value);
      console.log('playerIds:', playerIds);
      try {
        
        const response = await axios.post('/baseball/get-multiple-player-stats', playerIds);
        const stats = response.data;
        console.log('stats:', stats);
        batters.value.forEach(player => {
          console.log('player loaded:', player);
          if (stats[player.key_mlbam]) {
            console.log('player.key_mlbam:', player.key_mlbam);
            const processedStats = {
              all: {
                ...processStats(stats[player.key_mlbam].all || {}, fields.value.basic),
                ...processStats(stats[player.key_mlbam].all || {}, fields.value.custom)
              },
              days7: {
                ...processStats(stats[player.key_mlbam]['7'] || {}, fields.value.basic),
                ...processStats(stats[player.key_mlbam]['7'] || {}, fields.value.custom)
              },
              days14: {
                ...processStats(stats[player.key_mlbam]['14'] || {}, fields.value.basic),
                ...processStats(stats[player.key_mlbam]['14'] || {}, fields.value.custom)
              },
              days30: {
                ...processStats(stats[player.key_mlbam]['30'] || {}, fields.value.basic),
                ...processStats(stats[player.key_mlbam]['30'] || {}, fields.value.custom)
              },
              all_ranks: {
                ...stats[player.key_mlbam]['all_percentile_ranks'] || {}
              }, 
              days7_ranks: {
                ...stats[player.key_mlbam]['7_percentile_ranks'] || {}
              },
              days14_ranks: {
                ...stats[player.key_mlbam]['14_percentile_ranks'] || {}
              },
              days30_ranks: {
                ...stats[player.key_mlbam]['30_percentile_ranks'] || {}
              },
            };
            console.log('processedStats:', processedStats);
            player.stats = processedStats;  
            player.isLoading = false; // Loading done
          } else {
            console.error(`No stats found for player ${player.key_mlbam}`);
            player.stats = { all: {}, days7: {}, days14: {}, days30: {} };
          }
        });
      } catch (error) {
        console.error('Error fetching stats for players:', error);
        batters.value.forEach(player => {
          player.stats = { all: {}, days7: {}, days14: {}, days30: {} }; // Reset stats on error
        });
      } finally {
        loadingData.value = false;
        console.log('batters:', batters.value);
      }
    }

    function processStats(stats, fields) {
      return Object.fromEntries(
        Object.entries(stats).filter(([key]) => 
          fields.some(field => field.key === key)).map(([key, value]) => {
          if (key.includes('%')) {
            value = `${(value * 100).toFixed(1)}%`;
          } else if (typeof value === 'number' && !Number.isInteger(value)) {
            value = value
          }
          return [key, value];
        })
      );
    }
    function handlePlayerChipsUpdate(player_added) {
      console.log('Updated player selected :', player_added);
      const playerExists = selectedPlayersChips.value.some(player => player.key_mlbam === player_added.key_mlbam)
        
        if (!playerExists) {
            selectedPlayersChips.value.push(player_added)
            console.log('Selected player been added to selectedPlayersChips:', player_added)
        } else {
            console.log('Player already selected:', player_added)
        }
    }

    function removePlayerChip(player) {
        console.log('Removing player :', player);
        console.log('selectedPlayersChips length:', selectedPlayersChips.value.length);
        console.log('Attempting to remove player ID:', player.key_mlbam);
        selectedPlayersChips.value.forEach(p => console.log('Current player ID in array:', p.key_mlbam));
        selectedPlayersChips.value = selectedPlayersChips.value.filter(p => {
          const isMatch = p.key_mlbam !== player.key_mlbam;
          console.log(`Checking player ID: ${p.key_mlbam}, Remove: ${!isMatch}`);
          return isMatch;
        });
        console.log('selectedPlayersChips length after:', selectedPlayersChips.value.length);
        console.log('batters length:', batters.value.length);
        batters.value = batters.value.filter(p => {
          const isMatch = p.key_mlbam !== player.key_mlbam;
          console.log(`Checking player ID: ${p.key_mlbam}, Remove: ${!isMatch}`);
          return isMatch;
        });
        console.log('batters length after:', batters.value.length);
      }
      
    return {
      advanced,

      rankings,
      selectedDate,
      loadingData,
      dates,
      isPageLoading,
      selectedPlayersChips,
      handlePlayerChipsUpdate,
      removePlayerChip,
      fields,
      fetchStatsAllPlayers,
      filteredData,
      getStatModel,
      activeStatPeriod,
      setStatPeriod,
      computedSelectedPlayersChips
    }
  
  }
})
</script>
