<template>
  <div class="card">
    <TabView lazy>
      <TabPanel header="Stat Percentiles">
        <TeamPercentiles  />
      </TabPanel>
      <TabPanel header="Recent Video Replays">
        <TeamVideos  />
      </TabPanel>
      <TabPanel header="Statistics" ">
        <TeamStats  />
      </TabPanel>
      <TabPanel header="Performance" v-if="isAdmin">
        <TeamPerformance  v-if="isAdmin"/>
      </TabPanel>
    </TabView>
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