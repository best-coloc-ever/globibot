<server>

  <span> { name } <img src={ iconUrl }></span>

  <style scoped>
    img {
      max-width: 32px;
      max-height: 32px;
    }
  </style>

  <script>
    import API from '../api.js'

    this.name = '# ' + opts.snowflake;
    this.iconUrl = '//fakeimg.pl/300/?text=?'

    this.fetchServer = () => {
      if (opts.snowflake) {
        API.server(opts.snowflake)
          .then(data => {
            this.name = data.name
            this.iconUrl = data.icon_url
            this.update()
          })
      }
    }

    this.on('mount', () => {
      if (opts.name && opts.iconUrl) {
        this.name = opts.name
        this.iconUrl = opts.iconUrl
      }
      else
        this.fetchServer()
    })
  </script>

</server>
