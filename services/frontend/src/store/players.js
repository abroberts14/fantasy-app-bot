import axios from 'axios';
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

const  fields = {
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
    }

const dates = [
    { name: 'Season', code: 'all' },
    { name: '7 Day', code: 'days7' },
    { name: '14 Day', code: 'days14' },
    { name: '30 Day', code: 'days30' }
    ]

export const usePlayersStore = defineStore('players',  {
  id: 'players',
 
  state: () => ({
    player: {},
    players: [],
    loadingPlayers: false
  }),
  getters: {
    statePlayer: state => state.player,
    IsPlayerLoading: state => state.player.isPlayerLoading,
    statePlayers: state => state.players,
    stateLoadingPlayers: state => state.loadingPlayers
  },
  actions: {
        getPlayerFields() {
        return fields;
      },
      getPlayerDates() {
        return dates;
      },
      getPlayers() {
        return this.players;
      },
      async  fetchPlayerStats(playerId) {

        this.player.isPlayerLoading = true;
        this.loadingPlayers = true;
        let currentPlayer = {  }
        axios.get(`/baseball/get-player-name/${playerId}`).then(nameResponse => {
            if (!this.player.name) {
                this.player = { ...this.player, name: nameResponse.data };
            }
        }).catch(error => {
            console.error('Error fetching player name:', error);
        });
        try {
            const response = await axios.post('/baseball/get-multiple-player-stats', [playerId]);
            const stats = response.data;
            currentPlayer.name = stats[playerId].all.Name;
            this.player = {
                name: currentPlayer.name,
            };
            if (stats[playerId]) {
                const processedStats = this.getPlayerProcessesStats(stats[playerId]);
                console.log('processedStats:', processedStats);
                currentPlayer.stats = processedStats;
            } else {
                console.error(`No stats found for player ${playerId}`);
                currentPlayer.stats = { all: {}, days7: {}, days14: {}, days30: {} };
            }
        } catch (error) {
            console.error('Error fetching stats for player:', error);
            currentPlayer.stats = { all: {}, days7: {}, days14: {}, days30: {} }; // Reset stats on error
        } finally {

            this.player.isPlayerLoading = false;
            this.loadingPlayers = false;
            console.log('currentPlayer:', currentPlayer);
            this.player = {
                stats: currentPlayer.stats,
            };

        }
    },
     
    async  fetchAllPlayerStats(playerIds) {

        this.loadingPlayers = true;
        let currentPlayers = []
            // Asynchronously fetch names for all player IDs
        const namePromises = playerIds.map(playerId => 
            axios.get(`/baseball/get-player-name/${playerId}`)
                .then(response => {
                    console.log('Name response:', response); // Log the response
                    return {
                        key_mlbam: playerId,
                        name: response.data,
                        stats: {}  // Placeholder for stats
                    };
                })
                .catch(error => {
                    console.error(`Error fetching name for player ${playerId}:`, error);
                    return { key_mlbam: playerId, name: 'Unknown', stats: {} };
                })
        );
        try {
            // Resolve all name fetch promises
            currentPlayers = await Promise.all(namePromises);
            this.players = currentPlayers;
          
            const response = await axios.post('/baseball/get-multiple-player-stats', playerIds);
            const stats = response.data;
            
           
            playerIds.forEach(playerId => {
                let currentPlayerIndex = currentPlayers.findIndex(player => player.key_mlbam === playerId);
                let currentPlayer = currentPlayerIndex !== -1 ? currentPlayers[currentPlayerIndex] : { key_mlbam: playerId, stats: {} };

                if (stats[playerId]) {
                    const processedStats = this.getPlayerProcessesStats(stats[playerId]);
                    console.log('processedStats:', processedStats);
                    currentPlayer.stats = { ...currentPlayer.stats, ...processedStats };
                } else {
                    console.error(`No stats found for player ${playerId}`);
                    currentPlayer.stats = { ...currentPlayer.stats, all: {}, days7: {}, days14: {}, days30: {} };
                }

                if (currentPlayerIndex === -1) {
                    currentPlayers.push(currentPlayer);
                } else {
                    currentPlayers[currentPlayerIndex] = currentPlayer;
                }
            });
    

        } catch (error) {
            console.error('Error fetching stats for player:', error);
            
            currentPlayer.stats = { all: {}, days7: {}, days14: {}, days30: {} }; // Reset stats on error
        } finally {

            console.log('currentPlayer:', currentPlayers);
            this.players = currentPlayers;
            this.loadingPlayers = false;
            


        }
    },   
    getPlayerProcessesStats(stats) {
        const fields = this.getPlayerFields(); // Ensure fields is accessible
        console.log('fields:', fields);
        return  {
            all: {
                ...this.processStats(stats.all || {}, fields.basic),
                ...this.processStats(stats.all || {}, fields.custom)
            },
            days7: {
                ...this.processStats(stats['7'] || {}, fields.basic),
                ...this.processStats(stats['7'] || {}, fields.custom)
            },
            days14: {
                ...this.processStats(stats['14'] || {}, fields.basic),
                ...this.processStats(stats['14'] || {}, fields.custom)
            },
            days30: {
                ...this.processStats(stats['30'] || {}, fields.basic),
                ...this.processStats(stats['30'] || {}, fields.custom)
            },
            all_ranks: {
                ...stats['all_percentile_ranks'] || {}
            },
            days7_ranks: {
                ...stats['7_percentile_ranks'] || {}
            },
            days14_ranks: {
                ...stats['14_percentile_ranks'] || {}
            },
            days30_ranks: {
                ...stats['30_percentile_ranks'] || {}
            },
        };
    },
    processStats(stats, fields) {
        return Object.fromEntries(
            Object.entries(stats).filter(([key]) => 
                fields.some(field => field.key === key)).map(([key, value]) => {
                if (key.includes('%')) {
                    value = `${(value * 100).toFixed(1)}%`;
                }
     
                return [key, value];
                })
            );
    },
    setPlayers(players) {
        this.players = players;
    },
    removePlayerById(playerId) {
        this.players = this.players.filter(player => player.key_mlbam !== playerId);
    },
    removeAllPlayers() {
        this.players = [];
    }
  },
  
  persist: {
    enabled: true, // Enable persistence
    strategies: [
        {
          storage: localStorage, // Using localStorage to persist the data
          paths: ['players', 'player'] // Specify parts of the state to persist
        }
      ]
  },
  
  
});

export default usePlayersStore;