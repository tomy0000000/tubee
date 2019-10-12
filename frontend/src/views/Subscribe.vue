<template>
  <b-form @submit="onSubmit" v-if="show">
    <b-form-group id="channel-id-input-group-2" label="YouTube Channel ID" label-for="channel-id-input">
      <b-form-input id="channel-id-input" v-model="form.channelId" required placeholder="YouTube Channel ID"></b-form-input>
    </b-form-group>
    <b-button type="submit" variant="primary">Subscribe</b-button>
  </b-form>
</template>
<script>
export default {
  data () {
    return {
      form: {
        channelId: ''
      },
      show: true
    }
  },
  methods: {
    onSubmit (evt) {
      evt.preventDefault()
      alert(JSON.stringify(this.form))
    }
  }
}

</script>
