<template>
  <div class="w-full">
    
    <div v-if="drawerIsVisible">

      <div class="flex align-items-start justify-content-between  ">
        <div class="flex align-items-center justify-content-start flex-wrap  w-6 mr-1">
          <div class="flex justify-center w-full relative">

            <VirtualScroller ref="virtualScroller" :items="computedSelectedPlayersChips" :key="virtualKey"  @scroll="handleScrollIndexChange"   :emit-update="true" :itemSize=60 class="w-full  border-top-1 border-round-sm h-9rem sm:h-10rem md:h-15rem lg:h-15rem xl:h-15rem"  style=" border-color: rgba(0, 0, 0, 0.1);" >
              <template v-slot:item="{ item, options }">
                <div :class="['flex items-center  p-1 gap-1 w-full h', { 'bg-surface-100 dark:bg-surface-700': options.odd }]" style="height: 60px">
                  <!-- <div class="name-image-container">
                    <img class="img-headshot" :src="`https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_213,q_auto:best/v1/people/${item.key_mlbam}/headshot/67/current`" :alt="item.name" />
                  </div> -->

                    <Chip :removable="!playersLoading" class="font-medium text-sm w-full sm:w-10rem md:w-10rem lg:w-10rem xl:w-10rem"   @remove="removePlayerChip(item)">
                      <span >
                        <img class=" border-circle w-2rem h-3rem flex align-items-center justify-content-center" :src="`https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_213,q_auto:best/v1/people/${item.key_mlbam}/headshot/67/current`" :alt="item.name" />
                        
                      </span>
                      <span class="ml-2 font-medium">{{ item.name }}</span>

                      
                    </Chip>

                </div>

              </template>
            </VirtualScroller>
<!-- 
            <div 
            v-if="computedSelectedPlayersChips.length > 2" 
              class="fadeoutdown animation-duration-2000 animation-delay-500 animation-iteration-infinite flex align-items-end justify-content-end  absolute  transform -translate-x-1/2 " 
              style="z-index: 10; bottom:20%; right:8%"
            >
              <i class="pi pi-arrow-down">{{currentScrollIndex}}</i>
          </div> -->
          <div 
            v-if="computedSelectedPlayersChips.length > 2 && atBottom" 
            class="fadeoutup animation-duration-2000 animation-delay-500 animation-iteration-infinite flex align-items-start justify-content-end absolute transform -translate-x-1/2"
            style="z-index: 10; top: 20%; right: 8%"
          >
            <i class="pi pi-arrow-up"></i>
          </div>
          <div 
            v-if="computedSelectedPlayersChips.length > 2 && atTop" 
            class="fadeoutdown animation-duration-2000 animation-delay-500 animation-iteration-infinite flex align-items-end justify-content-end absolute transform -translate-x-1/2"
            style="z-index: 10; bottom: 20%; right: 8%"
          >
            <i class="pi pi-arrow-down"></i>
          </div>


          </div>
          
        </div>

        <div class="flex flex-wrap justify-content-start  w-6 ml-1">
            
            <SearchPlayers @playerSelected="handlePlayerChipsUpdate" :disabled="playersLoading || selectedPlayersChips.length >= 4" />
            <Select v-model="selectedDate" inputId="daterange" :options="dates" :disabled="playersLoading" optionLabel="name" placeholder="Dates" class="w-full mt-2"/>
            

  
            <div class="flex flex-wrap align-items-center justify-content-end w-full ">
              <ConfirmPopup>              
    
              </ConfirmPopup>
              <Button icon="pi pi-times" @click="confirm2($event)" :disabled="playersLoading" severity="danger" text raised rounded aria-label="Cancel" class="mt-2 mr-2" />
              
              <Button @click="fetchPlayers" class="mt-2" :disabled="playersLoading || selectedPlayersChips.length == 0">Compare</Button>
              <!-- <Button @click="fetchStatsAllPlayers" class="mt-2" :disabled="loadingData">Compare</Button> -->
              <Button  icon="pi pi-arrow-up" @click="drawerIsVisible = !drawerIsVisible" class="mt-2 ml-2" />
            </div>
        </div>
        
      </div>
    </div> 
    <div v-else class="flex align-items-center justify-content-between">
      <Select v-model="selectedDate" inputId="daterange" :options="dates" :disabled="playersLoading" optionLabel="name" placeholder="Dates" class="w-4 mt-2"/>

      <Button   label="Show options" icon="pi pi-bars" iconPos="right"  @click="drawerIsVisible = !drawerIsVisible" class="q-4" />

    </div>
    <Divider type="solid" class="mt-2"/>

    <DataTable v-show="batters.length > 0" :value="transposedData" :loading="playersLoading && (batters.length !== computedSelectedPlayersChips.length)" showGridlines removableSort class="compact-table" stripedRows scrollable :scrollHeight="tableScrollHeight">
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
          <Skeleton v-if="playersLoading" animation="wave" width="2rem" class="mb-2"/>

          <span v-else>{{ slotProps.data[col.field].value }}</span>
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
import { defineComponent, ref, computed, watch, onMounted, nextTick } from 'vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import axios from 'axios'
import SearchPlayers from '@/components/SearchPlayers.vue'
import ColorfulBadge from '@/components/ColorfulBadge.vue'
import { useConfirm } from "primevue/useconfirm";
import { useToast } from 'vue-toastification';
import { usePlayersStore } from '@/store/players';

export default defineComponent({
  name: 'ComparisonView',
  components: {
    LoadingSpinner,
    SearchPlayers,
    ColorfulBadge
  },
  setup() {
    const usersStore = useUsersStore()

    const playersStore = usePlayersStore();
    const fields = playersStore.getPlayerFields();
    const dates = playersStore.getPlayerDates();
    const batters = computed(() => playersStore.statePlayers);
    const playersLoading = computed(() => playersStore.stateLoadingPlayers);


    const selectedDate = ref(null)
    const drawerIsVisible = ref(true);  // Default is true, showing the drawer initially
    const tableScrollHeight = computed(() => drawerIsVisible.value ? '55vh' : '80vh');
    const currentScrollIndex = ref(0);
    const lastUpdated = ref(Date.now());


    const activeStatPeriod = ref('all');  // Default to all time stats


    const virtualScroller = ref(null);
    const confirm = useConfirm();
    const toast = useToast()
    const atTop = ref(true);
    const atBottom = ref(false);

    const virtualKey = ref(0);
    // Event handler for the scroll index change
    const handleScrollIndexChange = (newIndex) => {
      // console.log('Scroll index changed to:', newIndex);
      currentScrollIndex.value = newIndex;  // Update the current scroll index
      if (virtualScroller.value) {
        const range = virtualScroller.value.getRenderedRange();
       
        atTop.value = range.viewport.first === 0 && computedSelectedPlayersChips.value.length > range.viewport.last;
        atBottom.value = range.viewport.last === computedSelectedPlayersChips.value.length && range.viewport.first > 0;
      }
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
             
              playersStore.setPlayers([]);
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


    const transposedData = computed(() => {
      console.log('Last updated:', lastUpdated.value); // This line ensures lastUpdated is a dependency

      const fieldKeys = [
        ...fields.basic.map(f => f.key),
        ...fields.custom.map(f => f.key)
      ];

      const newRows = fieldKeys.map(field => {
        setStatPeriod(activeStatPeriod.value);
        const row = {
          stat: field,
          ...batters.value.reduce((acc, player) => {
           // console.log('f:', field)
            const key_mlbam = player.key_mlbam;
          
            const stats = player.stats && player.stats[activeStatPeriod.value] ? player.stats[activeStatPeriod.value] : {};
            const ranks = player.stats && player.stats[activeStatPeriod.value + '_ranks'] ? player.stats[activeStatPeriod.value + '_ranks'] : {};
            if (playersLoading.value  ) {
              acc[player.name] = {
                key_mlbam: key_mlbam,
             };
            }
              acc[player.name] = {
              key_mlbam: key_mlbam,
              value: stats[field] !== undefined ? stats[field] : '-',
              rank: ranks[field] !== undefined ? `${ranks[field]}` : '-' // Ensure ranks are properly accessed
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
    

    const setStatPeriod = (period) => {
      activeStatPeriod.value = period;
    };

    watch(playersLoading, (newVal) => {
      saveToLocalStorage();
    });
    // Watch for changes in selectedPlayersChips and log them
    watch(selectedPlayersChips, (newVal) => {
      saveToLocalStorage();

    });
    watch(drawerIsVisible, (newVal) => {
      saveToLocalStorage();
    });
    // Watch for changes in selectedDate
    watch(selectedDate, (newDate, oldDate) => {
        if (newDate) {
          setStatPeriod(newDate.code);
          saveToLocalStorage();
        }
    });
    async function fetchPlayers() {

      await playersStore.fetchAllPlayerStats(computedSelectedPlayersChips.value.map(player => player.key_mlbam));
    }

    function handlePlayerChipsUpdate(player_added) {
      console.log('Updated player selected :', player_added);
      const playerExists = selectedPlayersChips.value.some(player => player.key_mlbam === player_added.key_mlbam)
        
        if (!playerExists) {
            selectedPlayersChips.value.push(player_added)  // Add to the top of the list
            console.log('Selected player been added to selectedPlayersChips:', player_added)
        } else {
            console.log('Player already selected:', player_added)
        }
        saveToLocalStorage();
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
        console.log('batters:', batters.value);
        console.log('selectedPlayersChips length after:', selectedPlayersChips.value.length);
        console.log('batters length:', batters.value.length);
        playersStore.removePlayerById(player.key_mlbam);
        console.log('batters length after:', batters.value.length);
        virtualKey.value = virtualKey.value + 1;

      }
      
      function saveToLocalStorage() {
        const data = {
          selectedPlayersChips: selectedPlayersChips.value,
          activeStatPeriod: activeStatPeriod.value,
          selectedDate: selectedDate.value,
          drawerIsVisible: drawerIsVisible.value,
          batters: playersStore.getPlayers()
        };
        console.log('data:', data)
        localStorage.setItem('comparisonViewData', JSON.stringify(data));
      }

      function loadFromLocalStorage() {
        const data = JSON.parse(localStorage.getItem('comparisonViewData'));
        if (data) {
          console.log('data on load :', data)
          setStatPeriod(data.activeStatPeriod || 'all');
          selectedDate.value = data.selectedDate || null;
          drawerIsVisible.value = data.drawerIsVisible !== undefined ? data.drawerIsVisible : true;
          console.log("selectedPlayersChips.value:", data.selectedPlayersChips)
          playersStore.setPlayers(data.batters || []);
          selectedPlayersChips.value = data.selectedPlayersChips || [];
          console.log('playersStore players:', playersStore.players)
          console.log('batters end:', batters.value)
          console.log("selectedPlayersChips.value:", selectedPlayersChips.value)
          console.log("computedSelectedPlayersChips.value:", computedSelectedPlayersChips.value)
          console.log("playersLoading:", playersLoading.value)

          lastUpdated.value = Date.now(); // Update the timestamp to force reactivity
          virtualKey.value = virtualKey.value + 1;
        }
      }

    onMounted(() => {
      loadFromLocalStorage();
    });

    return {
      confirm2,
      selectedDate,
      dates,
      selectedPlayersChips,
      handlePlayerChipsUpdate,
      removePlayerChip,
      fields,
      getStatModel,
      activeStatPeriod,
      setStatPeriod,
      computedSelectedPlayersChips,
      transposedData,
      dynamicColumns,
      drawerIsVisible,
      tableScrollHeight,
      currentScrollIndex,
      virtualScroller,
      handleScrollIndexChange,
      atTop,
      atBottom,
      virtualKey,
      fetchPlayers,
      batters,
      playersLoading
    }
  
  }
})
</script>
