(function() {
  var game_data;
  var templates = {};

  // document.ready
  $(function() {
    // compile templates
    ['resource', 'building', 'upgrade'].foreach(function(ele) {
      templates[ele] = Handlebars.compile($('#' + ele + "_template").text());
    });
    $.ajax({
      type: 'GET',
      url: '/test/',  // TODO update this url
      dataType: 'json',
    }).done(function(data) {
      game_data = data;
      redraw_game();
      setInterval(update_resources(game_data), 100);
    });
  });


  $('section').on('click', 'li', function(){
    if (this.class === 'building' || this.class === 'upgrade') {
      $.ajax({
        type: 'POST',
        url: '/test/',  // TODO update this url
        contentType: 'application/json',
        data: {
          csrfmiddlewaretoken: getCookie('csrftoken'),
          clicked: this.class,
          name: this.id,
        },
        dataType: 'json'
      }).done(function(data) {
        game_data = data;
        redraw_game();
      });
    };
  });


  // From Django AJAX page:  https://docs.djangoproject.com/en/1.9/ref/csrf/#ajax
  function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
        var cookie = jQuery.trim(cookies[i]);
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) == (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  /* delete all the objects on the page and remake them
  with our new game data */
  function redraw_game() {
    // mark the game data with the time it arrived
    game_data.time = new Date().getTime() / 1000;
    // delete and redraw resources
    $('#resource_ul').clear();
    game_data.resources.foreach(function(resource) {
      resource.displayed = resource.owned;
      draw_element(resource, 'resource');
    });
    // delete and redraw buildings
    $('#building_ul').clear();
    game_data.buildings.foreach(function(building) {
      draw_element(building, 'building');
    });
    // delete and redraw upgrades
    $('#upgrade_ul').clear();
    game_data.upgrades.foreach(function(upgrade) {
      draw_element(upgrade, 'upgrade');
    });
  }

  //  draw element into page.  template name defaults to element name
  function draw_element(data, element) {
    data.element = $(templates[element](data));
    $('#' + element + '_ul').append(data.element);
  }

  // callback for our timer to animate resource values
  function update_resources() {
    // calculate elapsed time
    current_time = new Date().getTime() / 1000;
    time_passed = current_time - game_data.time;
    // replace the resource amounts in the dom elements with the
    // value at our current time
    game_data.resources.foreach(function(resource) {
        resource.element.find('.displayed').text(calc_resource(resource));
    });
  }

  /* calculate the amount of resources we have now, a given amount
  of time after the game data was last updated */
  function calc_resource(resource, time_passed) {
    current_amount = resource.owned + time_passed * resource.income;
    if (current_amount < 0) {
      current_amount == 0;
    } else if (resource.maximum !== null && current_amount > resource.maximum) {
      current_amount = resource.maximum;
    }
    return current_amount
  }

});
