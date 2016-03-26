<channel>

  <h4>{ name } ({ id })</h4>

  <ul>
    <li each={ message in messages }>{ message.author.name }: { message.content }</li>
  </ul>

  <script>
    this.name = opts.data.name;
    this.id = opts.data.id;
    this.messages = [];

    onMessage(message) {
      this.messages.push(message);
      this.update();
    }
  </script>

</channel>
