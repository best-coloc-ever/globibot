<server>

  <span> { name } <img src={ iconUrl } if={ iconUrl }></span>

  <style scoped>
    img {
      max-width: 32px;
      max-height: 32px;
    }
  </style>

  <script>
    var self = this;
    this.name = '# ' + opts.snowflake;
    this.iconUrl = null

    this.fetchServer = () => {
      if (opts.snowflake) {
        // let headers = new Headers({
        //   'Authorization': 'Bearer ' + this.opts.app.token
        // })

        fetch('/bot/api/server/' + opts.snowflake)
          .then(r => r.json())
          .then(data => {
            self.name = data.name
            self.iconUrl = data.icon_url
            self.update()
          })
      }
    }

    this.on('mount', this.fetchServer)
  </script>

</server>
