(function() {
  var game_data;
  var templates = {};

  $(function() {
    $.get(
      url: '/test/',
      success: function(data) {
        game_data = data;
      },
      type: 'json',
    );
    [
      'resource',
      'building',
      'building_cost',
      'building_income',
      'upgrade',
      'upgrade_cost',
    ].foreach(function(ele) {
      templates[ele] = Handlebars.compile($('#' + ele + "_template").text());
    });
    draw_game(game_data);
    setInterval(update_resources(game_data), 100);
  });


  $('section').on('click', 'li', function(){
    if (this.class === 'building' || this.class === 'upgrade') {
      $.post(
        url: '/test/',
        data: {
          csrfmiddlewaretoken: getCookie('csrftoken'),
          clicked: this.class,
          name: this.id,
        },
        success: draw_game
      );
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

  function draw_game(game_data) {
    update_resources(game_data.resources, 'resource');
    update_buildings(game_data.buildings, 'building');
    update_upgrades(game_data.upgrades, 'upgrade');
  }

  // function draw_resource(data) {
  //   $('#resource_ul').append(render(data, 'resource'));
  // }

  //  draw element into page.  template name defaults to element name
  function draw_element(data, element) {
    $('#' + element + "_ul").append(render(data, element));
  }

  //  render function will construct full template name as '#' + template + '_template'
  // function draw_element(data, element, template = element) {
  //   $('#' + element + "_ul").append(render(data, template));
  // }


  // function draw_building(data, element) {
  //   $('#' + element + "_ul").append(render(data));
  //   for (var cost in data) {
  //     draw_element(cost, element + "cost")
  //   }
  //   for (var income in data) {
  //     draw_element(income, element + "income")
  //   }
  // }


  // callback for our timer to animate resource values
  function update_resources() {
    current_time = new Date().getTime() / 1000;
    time_passed = current_time - game_date.time;
    $('#resource_ul').clear();
    for (var resource in game_data.resources) {
      var cur_res = game_data.resources[resource]
      cur_res.displayed = calc_resource(cur_res, time_passed)
      // draw_resource(cur_res);
      draw_element(cur_res, 'resource');
      }
    }
  }
  function update_buildings() {
    $('#building_ul').clear();
    for (var building in game_data.buildings) {
      var cur_building = game_data.buildings[building]
        draw_element(cur_building, 'building');
      }
      for (var cost in game_data.buildings[building]) {
        draw_element(cost, 'building_cost')
      }
      for (var income in game_data.buildings[building]) {
        draw_element(income, 'building_income')
      }
    }
  }
  function update_upgrades() {
    $('#upgrade_ul').clear();
    for (var upgrade in game_data.upgrades) {
      var cur_upgrade = game_data.upgrades[upgrade]
        draw_element(cur_upgrade, 'upgrade');
      }
      for (var cost in game_data.upgrades[upgrade]) {
        draw_cost(cost, 'upgrade_cost')
      }
    }
  }


  function calc_resource(game_data, current_time, time_passed) {
    current_amount = resource.owned + time_passed * resource.income;
    if (current_amount < 0) {
      current_amount == 0;
    } elseif (resource.maximum !== null && current_amount > resource.maximum) {
      current_amount = resource.maximum;
    }
    return current_amount
  }


  var render = function(data, element) {
    return templates[element](data)
  };


});
