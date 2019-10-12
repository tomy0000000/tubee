<template>
  <div id="app">
    <!-- BEGIN HEADER -->
    <header>
      <NavBar username="Tomy" />
    </header>
    <!-- END HEADER -->
    <main role="main" class="flex-grow-1">
      <b-container class="mt-3">
        <!-- BEGIN CONTENT -->
        <router-view />
        <!-- END CONTENT -->
      </b-container>
    </main>
    <!-- BEGIN FOOTER -->
    <footer class="footer mt-auto py-3">
      <div class="container text-muted text-center">
        <span class="linebreak">Copyright © 2019 Tomy Hsieh.</span>
        <span class="linebreak">All rights reserved.</span>
      </div>
    </footer>
    <!-- ENG FOOTER -->
  </div>
</template>
<script>
import NavBar from '@/components/NavBar.vue'

export default {
  name: 'home',
  components: {
    NavBar
  }
}

</script>
<style lang="scss">
html {
  min-height: 100%;
  position: relative;

  body {
    margin-bottom: 60px;
  }

  footer {
    bottom: 0;
    width: 100%;
    position: absolute;
    height: 60px;
    background-color: #f5f5f5;

    span.linebreak {
      display: inline-block;
    }
  }
}

</style>
