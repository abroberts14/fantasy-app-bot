<template>
  <div class="card">
    <Tabs value="0" lazy>
      <TabList>
        <Tab value="0">Stat Percentiles</Tab>
        <Tab value="1">Recent Video Replays</Tab>
        <Tab value="2">Statistics</Tab>
      </TabList>
      <TabPanels>
        <TabPanel value="0">
          <TeamPercentiles  />
        </TabPanel>
        <TabPanel value="1">
          <TeamVideos  />
        </TabPanel>
        <TabPanel value="2">
          <TeamStats  />
        </TabPanel>
      
      </TabPanels>
    </Tabs>
  </div>
</template>

<script>
import { ref } from 'vue';
import TeamPercentiles from '@/components/TeamPercentiles.vue';
import TeamVideos from '@/components/TeamVideos.vue';
import TeamStats from '@/components/TeamStats.vue';
import TeamPerformance from '@/components/TeamPerformance.vue';
import useUsersStore from '@/store/users';

export default {
  name: 'MyTeam',
  components: {
    TeamPercentiles,
    TeamVideos,
    TeamStats,
    TeamPerformance
  },
  setup() {
    const activeTab = ref('percentiles'); // Default active tab
    const usersStore = useUsersStore();
    const isAdmin = usersStore.isAdmin;
    // Function to change tab
    function changeTab(tab) {
      console.log("Change tab", tab);
      activeTab.value = tab;
    }

    return {
      activeTab,
      changeTab,
      isAdmin
    };
  }
}
</script>