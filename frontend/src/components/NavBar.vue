<template>
  <div>
    <b-navbar toggleable="lg" type="dark" variant="dark">
      <b-navbar-brand :to="{ name: 'Dashboard'}">
        <img id="hero" src="@/assets/tubee_text.png" alt="Tubee logo">
      </b-navbar-brand>
      <b-navbar-toggle target="nav-collapse"></b-navbar-toggle>
      <b-collapse id="nav-collapse" is-nav>
        <b-navbar-nav>
          <b-nav-item :to="{ name: 'Dashboard'}">Dashboard</b-nav-item>
          <b-nav-item :to="{ name: 'Subscribe'}">Subscribe</b-nav-item>
          <b-nav-item :to="{ name: 'Explore'}">Explore</b-nav-item>
          <b-nav-item-dropdown text="User" right>
            <b-dropdown-item href="#">Login</b-dropdown-item>
            <b-dropdown-item href="#">Register</b-dropdown-item>
            <b-dropdown-item href="#">Setting</b-dropdown-item>
            <b-dropdown-item href="#">Logout</b-dropdown-item>
          </b-nav-item-dropdown>
          <b-nav-item-dropdown text="Admin" right>
            <b-dropdown-item href="#">Dashboard: Notification</b-dropdown-item>
            <b-dropdown-item href="#">Dashboard: Scheduler</b-dropdown-item>
            <b-dropdown-item href="#">Dashboard: Hub</b-dropdown-item>
            <b-dropdown-item href="#">Send Test Notification</b-dropdown-item>
          </b-nav-item-dropdown>
          <b-nav-item-dropdown text="Dev" right>
            <b-dropdown-item href="#">Sitemap</b-dropdown-item>
            <b-dropdown-item href="#">Dict: OS</b-dropdown-item>
            <b-dropdown-item href="#">Dict: System</b-dropdown-item>
            <b-dropdown-item href="#">Dict: Flask</b-dropdown-item>
            <b-dropdown-item href="#">Dict: Scheduler</b-dropdown-item>
            <b-dropdown-item href="#">Dict: User</b-dropdown-item>
          </b-nav-item-dropdown>
        </b-navbar-nav>
        <b-navbar-nav v-if="username !== null" class="ml-auto">
          <span class="navbar-text" id="username">
            Hello! {{ username }}
          </span>
        </b-navbar-nav>
      </b-collapse>
    </b-navbar>
  </div>
</template>
<script>
export default {
  name: 'NavBar',
  props: {
    username: {
      type: String,
      default: null
    }
  }
}
</script>
<style scoped lang="scss">
#hero {
  height: 2rem;
}
</style>
