<template>
  <div class="card">
    <TeamFeedComponent  />
  </div>
</template>

<script>
import { ref } from 'vue';
import useUsersStore from '@/store/users';
import TeamFeedComponent from '@/components/TeamFeed.vue';

export default {
  name: 'MyTeam',
  components: {

    TeamFeedComponent
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