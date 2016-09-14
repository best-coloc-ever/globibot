<message>

  <span>
    <img src={ data.server.icon_url }></img> #{ data.channel.name }
    <span style="font-size: x-small">{ new Date(data.stamp * 1000).toLocaleTimeString() }</span>
    <span if={ data.is_deleted } style="color: red">Deleted</span>
    <br>
    { data.content }
  </span>

  <style scoped>
    img {
      max-width: 32px;
      max-height: 32px;
    }
  </style>

  <script>
    this.data = opts.data

    this.on('mount', () => {

    })
  </script>

</message>
