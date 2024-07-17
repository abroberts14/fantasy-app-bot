<template>
      <AutoComplete
        v-model="selectedPlayer"
        :suggestions="players"
        :loading="loadingData"
        optionLabel="name"
        :delay="750"
        forceSelection
        placeholder="Search player..."
        @complete="searchPlayers"
        @item-select="onPlayerSelect"
        :dropdown="true"
        :disabled="disabled"
        id="search-player"
        class="w-full"
      >
      </AutoComplete>

  </template>
  
  <script>
  import { ref, watch } from 'vue'
  import axios from 'axios'
  
  export default {
    name: 'SearchPlayers',
    emits: ['playerSelected'],
    props: {
      disabled: {
        type: Boolean,
        default: false
      }
    },
    setup(props, { emit }) {
      const selectedPlayer = ref({ name: '', key_mlbam: 0 })
      const players = ref([])
      const selectedPlayersChips = ref([])
      const loadingData = ref(false)
        
      function searchPlayers(event) {
        if (!event.query.trim()) {
          players.value = []
          return
        }
        loadingData.value = true
        axios
          .get(`/baseball/players/?name=${encodeURIComponent(event.query)}`)
          .then((response) => {
            players.value = response.data.map((player) => ({
              name_first: player.name_first,
              name_last: player.name_last,
              name: `${player.name_first} ${player.name_last}`,
              key_mlbam: player.key_mlbam
            }))
            console.log('Formatted players:', players.value)
          })
          .catch((error) => console.error('Error fetching players:', error))
          .finally(() => (loadingData.value = false))
      }
  
      function onPlayerSelect(event) {
        console.log('Player selected:', event)

        emit('playerSelected', event.value);

       
            
        console.log('Selected player:', event.value)
        players.value = []
        selectedPlayer.value = { name: '', key_mlbam: 0 }
      }
      // Watch for changes in selectedPlayersChips and emit the updated value
      // watch(selectedPlayersChips, (newChips) => {
      //   console.log('Emitting chips:', newChips); // Add this line

      //   emit('update:selectedPlayersChips', newChips)
      // }, { deep: true });
      
  
      
      return {
        selectedPlayer,
        players,
        searchPlayers,
        onPlayerSelect,
        loadingData,
        selectedPlayersChips
      }
    }
  }
  </script>