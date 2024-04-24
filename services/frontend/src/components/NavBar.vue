<!-- <template>
  <header>
    <nav class="navbar navbar-expand-md navbar-dark bg-dark">
      <div class="container">
        <router-link class="navbar-brand" to="/">SRC Bot</router-link>
        <button
          class="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarCollapse"
          aria-controls="navbarCollapse"
          aria-expanded="false"
          aria-label="Toggle navigation"
        >
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarCollapse" ref="navbarCollapse">
          <ul v-if="isLoggedIn" class="navbar-nav me-auto mb-2 mb-md-0">
            <li class="nav-item">
              <router-link class="nav-link" to="/" @click.native="collapseNavbar">Home</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/dashboard" @click.native="collapseNavbar">Dashboard</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/profile" @click.native="collapseNavbar">My Profile</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/register-bot" @click.native="collapseNavbar">Register New Bot</router-link>
            </li>
            
            <li v-if="isAdmin" class="nav-item">
              <router-link class="nav-link" to="/admin" @click.native="collapseNavbar">Admin</router-link>
            </li>
              <li class="nav-item">
              <a class="nav-link" @click="logout" @click.native="collapseNavbar">Log Out</a>
            </li>
          </ul>
          <ul v-else class="navbar-nav me-auto mb-2 mb-md-0">
            <li class="nav-item">
              <router-link class="nav-link" to="/" @click.native="collapseNavbar">Home</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/register" @click.native="collapseNavbar">Register</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/login" @click.native="collapseNavbar">Log In</router-link>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  </header>
</template> -->



<template>
  <header>
    <nav class="navbar navbar-expand-md navbar-dark bg-dark">
      <div class="container">
        <router-link class="navbar-brand" to="/">SRC Bot</router-link>
        <button
          class="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarCollapse"
          aria-controls="navbarCollapse"
          aria-expanded="false"
          aria-label="Toggle navigation"
        >
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarCollapse" ref="navbarCollapse">

          <!-- Navbar items for logged-in users -->
          <ul v-if="isLoggedIn" class="navbar-nav me-auto align-items-center">
            <li class="nav-item">
              <router-link class="nav-link" to="/dashboard" @click.native="collapseNavbar">Dashboard</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/profile" @click.native="collapseNavbar">My Profile</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/register-bot" @click.native="collapseNavbar">Register New Bot</router-link>
            </li>                        <li v-if="isAdmin" class="nav-item">
              <router-link class="nav-link" to="/admin" @click.native="collapseNavbar">Admin</router-link>
            </li>
          </ul>
          <ul v-if="isLoggedIn" class="navbar-nav ms-auto align-items-center">
            <li class="nav-item">
              <a class="btn btn-secondary btn-sm" @click="logout" @click.native="collapseNavbar">Log Out</a>
            </li>
          </ul>
          <!-- Navbar items for logged-out users -->
          <ul v-else class="navbar-nav ms-auto align-items-center">
            <li class="nav-item">
              <router-link class="nav-link" to="/login" @click.native="collapseNavbar">Log In</router-link>
            </li>
            <li class="nav-item">
              <router-link class="btn btn-primary btn-sm" to="/register" @click.native="collapseNavbar">Register</router-link>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  </header>
</template>

<script>
import { defineComponent, ref, onMounted } from 'vue'
import useUsersStore from '@/store/users';
import { Collapse } from 'bootstrap'
export default defineComponent({
  name: 'NavBar',
  setup() {
    const usersStore = useUsersStore();
    const navbarCollapse = ref(null);
    let collapseInstance = null;

    onMounted(() => {
      if (navbarCollapse.value) {
        collapseInstance = new Collapse(navbarCollapse.value, {
          toggle: false
        });
      }
    });

    function collapseNavbar() {
      if (collapseInstance && navbarCollapse.value.classList.contains('show')) {
        collapseInstance.hide();
      }
    }

    return { usersStore, collapseNavbar, navbarCollapse };
  },
  computed: {
    isLoggedIn() {
      return this.usersStore.isAuthenticated;
    },
    isAdmin() {
      return this.usersStore.isAdmin;
    }
  },
  methods: {
    async logout() {
      await this.usersStore.logOut();
      this.$router.push('/');
    }
  }
})
</script>
<style scoped>
a {
  cursor: pointer;
}

</style>
