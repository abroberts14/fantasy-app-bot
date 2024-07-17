

<template>
  <LoadingSpinner v-if="loadingPlayers"/>
  <section>
    <div class="flex align-items-center justify-content-between mt-2 mb-4">
      <div class="flex align-items-center justify-content-start flex-wrap  ">
        <ToggleSwitch  v-model="advanced" :binary="true" inputId="advanced" name="advanced" :disabled="loadingData || rankings" />
        <label for="advanced" class="flex  justify-content-start m-2" :class="{'disabled-label': loadingData || rankings}">Advanced Stats</label>
        <div class="flex align-items-center justify-content-start ">
          <ToggleSwitch v-model="rankings" :binary="true" inputId="rankings" name="rankings" :disabled="loadingData" />
          <label for="rankings" class="flex  justify-content-start m-2 " :class="{'disabled-label': loadingData}">Percentile Rankings</label>
        </div>
      </div>

      <div class="inline-flex">
        <div class="hidden md:block">
          <Select v-model="selectedDate" inputId="daterange" :options="dates" :disabled="loadingData" optionLabel="name" placeholder="Select Date Range"
        checkmark />
        </div>
        <div class="block md:hidden">
          <Select v-model="selectedDate" inputId="daterange" :options="dates" :disabled="loadingData" optionLabel="name" placeholder="Dates"
        checkmark />
        </div>
      </div>
    </div>


    
      <DataTable v-show="filteredData.length > 0 && (!advanced && !rankings)" :value="filteredData" showGridlines class="compact-table" stripedRows scrollable>
        <Column field="name" header="Name" class="compact-column" frozen>
          <template #body="slotProps">
            <div class="name-image-container">
              <img :src="`https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_213,q_auto:best/v1/people/${slotProps.data.key_mlbam}/headshot/67/current`" :alt="slotProps.data.name" class="img-headshot" />
              <span>{{ slotProps.data.name }}</span>
            </div>
          </template>
        </Column>
        <!-- Dynamic Stats Fields Access -->
        
        <Column v-for="field in fields.basic" :key="field.key" :field="`stats.${activeStatPeriod}.` + field.key" :header="field.label" class="compact-column right-aligned">
          <template #body="slotProps">
            <Skeleton v-if="loadingData" animation="wave" width="2rem" class="mb-2"/>
            <span v-else>{{ getStatModel(slotProps, field.key) }}</span>
          </template>
        </Column>
      </DataTable>
      <DataTable v-show="filteredData.length > 0 && (advanced && !rankings)" :value="filteredData" showGridlines class="compact-table" stripedRows scrollable>
        <Column field="name" header="Name" class="compact-column" frozen>
          <template #body="slotProps">
            <div class="name-image-container">
              <img :src="`https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_213,q_auto:best/v1/people/${slotProps.data.key_mlbam}/headshot/67/current`" :alt="slotProps.data.name" class="img-headshot" />
              <span>{{ slotProps.data.name }}</span>
            </div>
          </template>
        </Column>
        <Column v-for="field in fields.custom"  :key="field.key" :field="`stats.${activeStatPeriod}.` + field.key" :header="field.label" class="compact-column right-aligned">
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
      <DataTable v-show="filteredData.length > 0 && rankings " :value="filteredData" showGridlines class="compact-table" stripedRows scrollable>
        <Column field="name" header="Name" class="compact-column" frozen>
          <template #body="slotProps">
            <div class="name-image-container">
              <img :src="`https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_213,q_auto:best/v1/people/${slotProps.data.key_mlbam}/headshot/67/current`" :alt="slotProps.data.name" class="img-headshot" />
              <span>{{ slotProps.data.name }}</span>
            </div>
          </template>
        </Column>
        <Column v-for="field in fields.percentiles"  :key="field.key" :field="`stats.${activeStatPeriod}.` + field.key" :header="field.label" class="compact-column right-aligned">
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
  </section>
</template>

<script>
import { defineComponent, ref, computed, onMounted, onUnmounted, watch } from 'vue';
import useUsersStore from '@/store/users';
import MediaPlayer from '@/components/MediaPlayer.vue';
import LoadingSpinner from '@/components/LoadingSpinner.vue';
import axios from 'axios';
import ModalOverlay from '@/components/ModalOverlay.vue';
import { useRouter } from 'vue-router';
import PercentileBars from '@/components/PercentileBars.vue';
import ColorfulBadge from '@/components/ColorfulBadge.vue';
export default defineComponent({
  name: 'TeamStatsView',
  components: {
    MediaPlayer,
    LoadingSpinner,
    ModalOverlay,
    PercentileBars,
    ColorfulBadge
  },
  setup() {
    const usersStore = useUsersStore();
    const selectedPlayer = ref({ name: '', id: 0 });
    const players = ref([]);
    const router = useRouter();
    const loadingData = ref(false);
    const loadingPlayers = ref(false);
    const batters = ref([]);
    const user = computed(() => usersStore.user);
    const isLoggedIn = computed(() => usersStore.isAuthenticated);
    const expandedRow = ref([]);
    const activeStatTab = ref('Basic Stats');
    const dynamicScrollHeight = ref('900px'); // Default value
    const selectedStatGroup = ref(null);
    const activeStatPeriod = ref('all');  // Default to all time stats
    const op = ref(null);
    const activeFields = ref([]);
    const advanced = ref(false);
    const rankings = ref(false);
    const selectedDate = ref();
    const dates = ref([
        { name: 'Season', code: 'all' },
        { name: '7 Day', code: 'days7' },
        { name: '14 Day', code: 'days14' },
        { name: '30 Day', code: 'days30' }
    ]);
    const getStatModel = (slotProps, key) => {
      const periodStats = slotProps.data.stats[activeStatPeriod.value];
      if (!periodStats) {
        slotProps.data.stats[activeStatPeriod.value] = {};
      }
      return periodStats[key] !== undefined ? periodStats[key] : null;

    };
    const toggle = (event) => {
      console.log('Cell clicked:', event);

      console.log(op.value);
      if (op.value && typeof op.value.toggle === 'function') {
        op.value.toggle(event);
      } else {
        console.error('Popover toggle method is not available');
      }
    };
    const setStatPeriod = (period) => {
      activeStatPeriod.value = period;
    };

    watch(advanced, (newAdvanced, oldAdvanced) => {
      if (newAdvanced) {
        activeFields.value = fields.value.custom;
      } else {
        activeFields.value = fields.value.basic;
      }
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

    watch(rankings, (newRankings, oldRankings) => {
        if (newRankings) {
          setStatPeriod(`${activeStatPeriod.value}_ranks`);
          activeFields.value = fields.value.percentiles;
        } else {
          if (advanced.value) {
            activeFields.value = fields.value.custom;
          } else {
            activeFields.value = fields.value.basic;
          }
          setStatPeriod('all');
        }
      
        console.log(activeStatPeriod.value);
        console.log(batters.value)
    });

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
    // const activeFilter = computed(() => {
    //   return batters.value.filter(player => player.stats[activeStatPeriod][activeStatTab]);
    // });
    const filteredData = computed(() => {
      return batters.value.map(player => ({
        ...player,
        stats: player.stats? player.stats : {}
      }));
    });


    onMounted(() => {
      fetchMyPlayers();
      updateScrollHeight();
      window.addEventListener('resize', updateScrollHeight); // Update on window resize
      window.scrollTo({
        top: 0, // Adjust this value to position the scroll appropriately
        behavior: 'smooth'
      });
      activeFields.value = fields.value.basic;
    });

    onUnmounted(() => {
      window.removeEventListener('resize', updateScrollHeight); // Clean up the event listener
    });

    async function fetchStatsAllPlayers() {
      loadingData.value = true;
      console.log('batters:', batters.value);
      const playerIds = batters.value.map(player => player.key_mlbam);
      try {
        const response = await axios.post('/baseball/get-multiple-player-stats', playerIds);
        const stats = response.data;
        loadingData.value = false;
        batters.value.forEach(player => {
          if (stats[player.key_mlbam]) {
            // player.stats = {
            //   all: stats[player.key_mlbam].all || {},
            //   days7: stats[player.key_mlbam]['7'] || {},
            //   days14: stats[player.key_mlbam]['14'] || {},
            //   days30: stats[player.key_mlbam]['30'] || {}
            // };
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
      }
    }
    async function fetchMyPlayers() {
      if (!isLoggedIn) {
        console.error('User is not logged in or token is not available');
        return;
      }
      loadingPlayers.value = true;
      try {
        const response = await axios.get('/baseball/players/my-players');
        batters.value = response.data.players.batters || [];
      } catch (error) {
        console.error('Failed to fetch players:', error);
        batters.value = [];
      } finally {
        loadingPlayers.value = false;
        console.log('batters after my player:', batters.value);
        fetchStatsAllPlayers();
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
    function updateScrollHeight() {
      const width = window.innerWidth;
      const height = window.innerHeight;
      // Adjust dynamicScrollHeight based on window dimensions if necessary
    }

    return {
      selectedPlayer,
      players,
      batters,
      isLoggedIn,
      fetchMyPlayers,
      dynamicScrollHeight,
      updateScrollHeight,
      loadingPlayers,
      fetchStatsAllPlayers,
      fields,
      selectedStatGroup,
      activeStatTab,
      filteredData,
      advanced,
      activeStatPeriod,
      loadingData,
      setStatPeriod,
      toggle,
      op,
      selectedDate,
      dates,
      rankings,
      getStatModel, 
      activeFields
    };
  }
});
</script>
   

  
  <style scoped>

  .card-settings {
    width: auto;;
    overflow:auto;
    
  }
  
  .settings-checkbox {
    margin: 0;
    display: flex;
    align-items: center;
  }
  
  .search-input,
  .dropdown-full-width {
    width: 100%;
  }
  
  .footer-buttons {
    display: flex;
    align-items: center; /* Center align the button and checkbox vertically */
    gap: 20px; /* Space between the button and the checkbox */
    text-align: center;
  
  }
  
  .footer-buttons .filter-checkbox {
    margin-left: 20px; /* Add more space between the button and the checkbox if needed */
  }
  .video-section {
    justify-content: center;
    align-items: center;
    height: 100vh;
    padding: auto;
  }
  
  .content-flex {
    display: flex;
    flex-direction: column;
    justify-content: space-evenly;
    align-items: center;
    height: 100%;  /* Adjust the height as necessary to fit your layout */
  }
  
  .settings-item {
    display: flex;
    align-items: center; /* Center align the button and checkbox vertically */
    gap: 20px; /* Space between the button and the checkbox */
    text-align: center;}
  
  
  .video-container {
    margin-bottom: 20px; /* Adjust the gap size as needed */
  }
  .loading-spinner {
    display: inline-block;
    vertical-align: middle;
    margin-left: 5px;
  }
  </style>
  


