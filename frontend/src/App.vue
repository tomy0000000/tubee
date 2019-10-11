<template>
  <div id="app">
    <NavBar username="tmp-user"/>
    <router-view />
  </div>
</template>

<script>
// @ is an alias to /src
import NavBar from '@/components/NavBar.vue'

export default {
  name: 'home',
  components: {
    NavBar
  }
}
</script>

<style lang="scss">
#app {
  text-align: center;
}

span.line {
    display: inline-block;
}

</style>
