

class Rainbow {
  private Integer[] rgb_array = {254, 0, 0};
  private Integer counter, decreasing_color, increasing_color, color_multiplier;

  Rainbow(int cm) {
    counter = 0;
    decreasing_color = 0;
    increasing_color = 0;
    color_multiplier = cm;
  }

  Integer[] getNextColor() {
    if (counter == 0) {
      if (increasing_color == 2) {
        increasing_color = 0;
      } else {
        increasing_color = decreasing_color + 1;
      }
    }

    counter += color_multiplier;
    rgb_array[decreasing_color] -= color_multiplier;
    rgb_array[increasing_color] += color_multiplier;

    if (counter >= 254) {
      counter = 0;
      decreasing_color += 1;
      if (decreasing_color >= 3) {
        decreasing_color = 0;
      }
    }
    //println("Rain ---> " + rgb_array[0].toString());
    return rgb_array;
  }

  void clearVariables() {
    rgb_array = new Integer[] {254, 0, 0};
    counter = 0;
    decreasing_color = 0;
    increasing_color = 0;
  }
}