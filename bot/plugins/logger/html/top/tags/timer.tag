<timer>

  <div>
    { fromNow(opts.value) } ago
  </div>

  <script>
    var self = this;

    var shortEnglishHumanizer = humanizeDuration.humanizer({
      language: 'shortEn',
      round: true,
      spacer: '',
      delimiter: ' ',
      languages: {
        shortEn: {
          y: function() { return 'y' },
          mo: function() { return 'mo' },
          w: function() { return 'w' },
          d: function() { return 'd' },
          h: function() { return 'h' },
          m: function() { return 'm' },
          s: function() { return 's' },
          ms: function() { return 'ms' },
        }
      }
    });

    fromNow(stamp) {
      var now = new Date().getTime();
      return shortEnglishHumanizer(Math.round(now - stamp));
    }

    this.on('mount', function() {
      setInterval(function() { self.opts.value += 1; self.update(); }, 1000);
    });
  </script>

</timer>
