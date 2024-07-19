<template>
  <div class="w-full">
    
    <div v-if="drawerIsVisible">

      <div class="flex align-items-start justify-content-between  ">
        <div class="flex align-items-center justify-content-start flex-wrap  w-6 mr-1">
          <div class="flex justify-center w-full relative">

            <VirtualScroller :items="computedSelectedPlayersChips"   @scroll-index-change="handleScrollIndexChange"   :emit-update="true" :itemSize=60 class="w-full  border-top-1 border-round-sm h-9rem sm:h-10rem md:h-15rem lg:h-15rem xl:h-15rem"  style=" border-color: rgba(0, 0, 0, 0.1);" >
              <template v-slot:item="{ item, options }">
                <div :class="['flex items-center  p-1 gap-1 w-full', { 'bg-surface-100 dark:bg-surface-700': options.odd }]">
                  <!-- <div class="name-image-container">
                    <img class="img-headshot" :src="`https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_213,q_auto:best/v1/people/${item.key_mlbam}/headshot/67/current`" :alt="item.name" />
                  </div> -->

                    <Chip :removable="!loadingData" class="font-medium text-sm w-full sm:w-10rem md:w-10rem lg:w-10rem xl:w-10rem"   @remove="removePlayerChip(item)">
                      <span >
                        <img class=" border-circle w-2rem h-3rem flex align-items-center justify-content-center" :src="`https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_213,q_auto:best/v1/people/${item.key_mlbam}/headshot/67/current`" :alt="item.name" />
                      </span>
                      <span class="ml-2 font-medium">{{ item.name }}</span>

                      
                    </Chip>

                </div>

              </template>
            </VirtualScroller>

            <div 
            v-if="computedSelectedPlayersChips.length > 2" 
            class="fadeoutdown animation-duration-2000 animation-delay-500 animation-iteration-infinite flex align-items-end justify-content-end  absolute  transform -translate-x-1/2 " 
            style="z-index: 10; bottom:20%; right:8%"
          >
              <i class="pi pi-arrow-down"></i>
          </div>



          </div>
          
        </div>

        <div class="flex flex-wrap justify-content-start  w-6 ml-1">
            
            <SearchPlayers @playerSelected="handlePlayerChipsUpdate" :disabled="loadingData || selectedPlayersChips.length >= 4" />
            <Select v-model="selectedDate" inputId="daterange" :options="dates" :disabled="loadingData" optionLabel="name" placeholder="Dates" class="w-full mt-2"/>
            

  
            <div class="flex flex-wrap align-items-center justify-content-end w-full ">
              <ConfirmPopup>              
    
              </ConfirmPopup>
              <Button icon="pi pi-times" @click="confirm2($event)" :disabled="loadingData" severity="danger" text raised rounded aria-label="Cancel" class="mt-2 mr-2" />

              <Button @click="fetchStatsAllPlayers" class="mt-2" :disabled="loadingData">Compare</Button>
              <Button  icon="pi pi-arrow-up" @click="drawerIsVisible = !drawerIsVisible" class="mt-2 ml-2" />
            </div>
        </div>
        
      </div>
    </div> 
    <div v-else class="flex align-items-center justify-content-between">
      <Select v-model="selectedDate" inputId="daterange" :options="dates" :disabled="loadingData" optionLabel="name" placeholder="Dates" class="w-4 mt-2"/>

      <Button   label="Show options" icon="pi pi-bars" iconPos="right"  @click="drawerIsVisible = !drawerIsVisible" class="q-4" />

    </div>
    <Divider type="solid" class="mt-2"/>

    <DataTable v-show="filteredData.length > 0 " :value="transposedData" showGridlines removableSort class="compact-table" stripedRows scrollable :scrollHeight="tableScrollHeight">
        <!-- <Column v-for="(col, index) in dynamicColumns" :key="index" :field="col.field" :header="col.header" :frozen="index === 0" class="compact-column w-min">
          <template #body="slotProps">
            <span>{{ slotProps.data[col.field] }}</span>
            

          </template>
        </Column> -->
        <Column frozen field="stat" header="Stat" class="compact-column w-min">
          <template #body="slotProps">
            <span class="font-semibold	">{{ slotProps.data.stat }}</span>
          </template>
        </Column>
      <Column v-for="(col, index) in dynamicColumns" :key="index" :field="col.field"  class="compact-column ">
        <template #header>
          <div class="name-image-container  ">
              <img :src="`https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_213,q_auto:best/v1/people/${col.key_mlbam}/headshot/67/current`" :alt="col.header" class="img-headshot" />
              <span>{{ col.header }}</span>
            </div>
        </template>
        <template #body="slotProps">
        <div >
          <Skeleton v-if="loadingData" animation="wave" width="2rem" class="mb-2"/>

          <span v-else>{{ slotProps.data[col.field].value }}</span>
          <!-- <span v-if="slotProps.data[col.field].rank !== '-'"> ({{ slotProps.data[col.field].rank }})</span> -->
          <span class="flex flex-end w-full">
            <ColorfulBadge v-if="slotProps.data[col.field].rank !== '-'" :value="Number(slotProps.data[col.field].rank)" ></ColorfulBadge>
          </span>

        </div>
      </template>
    </Column>

    </DataTable>

  </div>

</template>


 <!-- HORIZONTAL TABLE
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
                <ColorfulBadge v-if="rankings" :value="slotProps.data.stats[activeStatPeriod][field.key]"></ColorfulBadge>

              </div>
            </div>
           
          </template>
        </Column>
      </DataTable> -->


<script>
import useUsersStore from '@/store/users'
import { defineComponent, ref, computed, watch, onMounted } from 'vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import axios from 'axios'
import SearchPlayers from '@/components/SearchPlayers.vue'
import ColorfulBadge from '@/components/ColorfulBadge.vue'
import { useConfirm } from "primevue/useconfirm";
import { useToast } from 'vue-toastification';

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
    const drawerIsVisible = ref(true);  // Default is true, showing the drawer initially
    const tableScrollHeight = computed(() => drawerIsVisible.value ? '55vh' : '80vh');
    const currentScrollIndex = ref(0);

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
    const confirm = useConfirm();
    const toast = useToast()
    // Event handler for the scroll index change
    const handleScrollIndexChange = (newIndex) => {
      console.log('Scroll index changed to:', newIndex);
      currentScrollIndex.value = newIndex;  // Update the current scroll index
    };
    const confirm2 = (event) => {
      confirm.require({
          target: event.currentTarget,
          message: 'Do you want to remove all players?',
          icon: 'pi pi-info-circle',
          rejectProps: {
              label: 'Cancel',
              severity: 'secondary',
              outlined: true
          },
          acceptProps: {
              label: 'Remove',
              severity: 'danger'
          },
          accept: () => {
              selectedPlayersChips.value = [];
              batters.value = [];
              saveToLocalStorage();
              toast.info('All players removed');
          },
          reject: () => {
              toast.add({ severity: 'error', summary: 'Rejected', detail: 'You have rejected', life: 3000 });
          }
      });
  };
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


    const transposedData = computed(() => {
      const fieldKeys = [
        ...fields.value.basic.map(f => f.key),
        ...fields.value.custom.map(f => f.key)
      ];

      const newRows = fieldKeys.map(field => {
        const row = {
          stat: field,
          ...filteredData.value.reduce((acc, player) => {
            const key_mlbam = player.key_mlbam;
            const stats = player.stats[activeStatPeriod.value];
            const ranks = player.stats[activeStatPeriod.value + '_ranks']; // Adjusting how ranks are accessed

            acc[player.name] = {
              key_mlbam: key_mlbam,
              value: stats && stats[field] ? stats[field] : '-',
              rank: ranks && ranks[field] ? `${ranks[field]}` : '-' // Ensure ranks are properly accessed
            };
            return acc;
          }, {})
        };
        return row;
      });
      return newRows;
    });


    const dynamicColumns = computed(() => {
      if (transposedData.value.length === 0) return [];
      const playerKeys = Object.keys(transposedData.value[0]).filter(key => key !== 'stat');
      const playerEntries = Object.entries(transposedData.value[0]).filter(([key]) => key !== 'stat');
      // Create columns for each player
      return playerEntries.map(([key, value]) => ({
        field: key,
        header: key,
        key_mlbam: value.key_mlbam // You can also transform this to more user-friendly names if needed
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
      saveToLocalStorage();

    });
    watch(drawerIsVisible, (newVal) => {
      console.log('drawerIsVisible updated:', newVal);
      saveToLocalStorage();

    });
    // Watch for changes in selectedDate
    watch(selectedDate, (newDate, oldDate) => {
        if (newDate) {
          if (rankings.value) {
            setStatPeriod(`${newDate.code}_ranks`);
          } else {
            setStatPeriod(newDate.code);
          }
          saveToLocalStorage();

        }
    });
    async function fetchStatsAllPlayers() {
      loadingData.value = true;
      // set batters to the computedchips
      console.log('selectedcomputedPlayersChips:', computedSelectedPlayersChips.value);

      batters.value = computedSelectedPlayersChips.value.map(player => ({ ...player }));
      drawerIsVisible.value = false;
      const playerIds = batters.value.map(player => player.key_mlbam);
      console.log('batters:', batters.value);
      console.log('playerIds:', playerIds);
      try {
        
        const response = await axios.post('/baseball/get-multiple-player-stats', playerIds);
        const stats = response.data;
        batters.value.forEach(player => {
          if (stats[player.key_mlbam]) {
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
        saveToLocalStorage();

      }
    }

    function processStats(stats, fields) {
      return Object.fromEntries(
        Object.entries(stats).filter(([key]) => 
          fields.some(field => field.key === key)).map(([key, value]) => {
          if (key.includes('%')) {
            value = `${(value * 100).toFixed(1)}%`;
          }
          // } else if (typeof value === 'number' && !Number.isInteger(value)) {
          //   value = value
          // }
          return [key, value];
        })
      );
    }
    function handlePlayerChipsUpdate(player_added) {
      console.log('Updated player selected :', player_added);
      const playerExists = selectedPlayersChips.value.some(player => player.key_mlbam === player_added.key_mlbam)
        
        if (!playerExists) {
            selectedPlayersChips.value.unshift(player_added)  // Add to the top of the list
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
      
      function saveToLocalStorage() {
        const data = {
          selectedPlayersChips: selectedPlayersChips.value,
          selectedDate: selectedDate.value,
          batters: batters.value,
          drawerIsVisible: drawerIsVisible.value
        };
        localStorage.setItem('comparisonViewData', JSON.stringify(data));
      }

      function loadFromLocalStorage() {
        const data = JSON.parse(localStorage.getItem('comparisonViewData'));
        if (data) {
          selectedPlayersChips.value = data.selectedPlayersChips || [];
          selectedDate.value = data.selectedDate || null;
          batters.value = data.batters || [];
          drawerIsVisible.value = data.drawerIsVisible !== undefined ? data.drawerIsVisible : true;
        }
      }

    onMounted(() => {
      loadFromLocalStorage();
    });

    return {
      advanced,
      confirm2,
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
      computedSelectedPlayersChips,
      transposedData,
      dynamicColumns,
      drawerIsVisible,
      tableScrollHeight,
      currentScrollIndex,
      handleScrollIndexChange
    }
  
  }
})
</script>
