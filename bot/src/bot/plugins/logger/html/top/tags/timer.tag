<timer>

  <div>
    ~ { fromNow(opts.value) } seconds ago
  </div>

  <script>
    var self = this;
    // this.seconds = fromNow(opts.value);

    fromNow(stamp) {
      var now = new Date().getTime() / 1000;
      return Math.round(now - stamp);
    }

    this.on('mount', function() {
      setInterval(function() { self.opts.value += 1; self.update(); }, 1000);
    });
  </script>

</timer>
