import processing.net.*;
import java.util.Random;
import java.util.Collections;

static Server s1, s2;
Settings settings;
Random rand;
Spectrum spectrum;

Rainbow rainbow = new Rainbow(1);

String[] DISPLAY_MODES;
String color_values;

Integer[] main_rgb_to_print, second_rgb_to_print, next_main_rgb_to_print, next_second_rgb_to_print, DISPLAY_MODE_INDIVIDUAL_TIMER_ARRAY;
Integer display_mode, display_mode_position, DISPLAY_MODE_DURATION;
int FPS, display_mode_time_counter, display_mode_counter, n1, n2, total_loop_passes;

Boolean frb = true;
int fr = 60;

void setup() {
  main_rgb_to_print = new Integer[] {255, 255, 255};
  second_rgb_to_print = new Integer[] {128, 128, 128};
  next_main_rgb_to_print = new Integer[] {255, 255, 255};
  next_second_rgb_to_print = new Integer[] {128, 128, 128};

  rand = new Random();
  n1 = rand.nextInt(8);
  n2 = rand.nextInt(8);

  spectrum = new Spectrum();
  settings = new Settings();

  display_mode_time_counter = 0;
  display_mode = 0;
  display_mode_counter = 1;
  DISPLAY_MODES = settings.getDisplayModes();
  DISPLAY_MODE_DURATION = 5;
  DISPLAY_MODE_DURATION = settings.getDisplayModeDuration();
  DISPLAY_MODE_DURATION = 5;
  DISPLAY_MODE_INDIVIDUAL_TIMER_ARRAY = settings.getDisplayModeTimer();


  FPS = 60;
  frameRate(FPS);


  try {
    s1 = new Server(this, 8080);
    s2 = new Server(this, 8081);
  } 
  catch(Exception ex) {
    println("Port in use! Exiting...");
    System.exit(0);
  }



  total_loop_passes = 0;
}

void draw() {
  frameRate(60);
  //println(fr);

  if (fr >= 60) frb = true;
  else if (fr <= 1) frb = false;

  if (frb) fr--;
  else fr++;

  spectrum.processSpectrumData();

  String string_to_send = spectrum.concatenateStringtoSend(total_loop_passes);
  //println(string_to_send);

  if (display_mode_time_counter >= DISPLAY_MODE_DURATION * FPS) {
    n1 = rand.nextInt(8);
    n2 = rand.nextInt(8);
    display_mode_time_counter = 0;

    if (display_mode_counter > DISPLAY_MODE_INDIVIDUAL_TIMER_ARRAY[display_mode_position]) {
      if (display_mode_position < DISPLAY_MODES.length) {
        display_mode = Integer.parseInt(DISPLAY_MODES[display_mode_position]);
      } else {
        display_mode_position = 0;
        display_mode = Integer.parseInt(DISPLAY_MODES[display_mode_position]);
      }
      display_mode_counter = 0;
      
      if(display_mode.equals("0") || display_mode.equals("2") || display_mode.equals("3")){
        next_main_rgb_to_print = getColorValues(n1);
        next_second_rgb_to_print = getColorValues(n2);
      }
      // else if (display_mode.equals("1")){
      //}
    }

    //switch(display_mode) {
    //case 0:
    //  if (display_mode_counter > 6) {
    //    // MAKE FUNCTION FOR DISPLAY MODE TO LOOP WHEN DONE 
    //    display_mode = 2;
    //    //rainbow.clearVariables();
    //    display_mode_counter = 0;
    //  } else {
    //    next_main_rgb_to_print = getColorValues(n1);
    //    next_second_rgb_to_print = getColorValues(n2);
    //    break;
    //  }

    //case 2:
    //  if (display_mode_counter > 3) {
    //    display_mode = 3;
    //    display_mode_counter = 0;
    //  } else {
    //    break;
    //  }

    //case 3:
    //  if (display_mode_counter > 3) {
    //    display_mode = 0;
    //    display_mode_counter = 0;
    //  }
    //  next_main_rgb_to_print = getColorValues(n1);
    //  next_second_rgb_to_print = getColorValues(n2);
    //  break;

    //default:
    //  if (display_mode_counter >= 3) {
    //    display_mode = 0;
    //    display_mode_counter = 0;
    //  }
    //  next_main_rgb_to_print = getColorValues(n1);
    //  next_second_rgb_to_print = getColorValues(n2);
    //  break;
    //}

    display_mode_counter++;
  } else {
    display_mode_time_counter++;
  }

  println("Next ---> " + getStringtoPrint(display_mode, next_main_rgb_to_print, next_second_rgb_to_print));

  // THIS CAUSES ERRORS
  if (display_mode == 0 || display_mode == 3) {
    main_rgb_to_print = calculateTransition(main_rgb_to_print, next_main_rgb_to_print);
    second_rgb_to_print = calculateTransition(second_rgb_to_print, next_second_rgb_to_print);
  } else if (display_mode == 2) {
    main_rgb_to_print = rainbow.getNextColor();
    second_rgb_to_print = main_rgb_to_print;
  }
  color_values = getStringtoPrint(display_mode, main_rgb_to_print, second_rgb_to_print);

  // AVG IS NOT SECOND IN THE LIST ANYMORE
  println("Cur ----> " + color_values);
  try {
    printServer(1, string_to_send + "n");
    printServer(2, color_values + "n");
  } 
  catch(Exception e) {
    println("Write failed!");
  }

  total_loop_passes++;
}


void stop() {
  // always close Minim audio classes when you finish with them
  spectrum.stopListing();
  s1.stop();
  s2.stop();
  super.stop();
}

//Integer[] getDisplayMode(){

//}

String getStringtoPrint(Integer display_mode, Integer[] current_rgb, Integer[] next_rgb) {
  ArrayList<Integer> all_rgbs = new ArrayList();
  Collections.addAll(all_rgbs, current_rgb);
  Collections.addAll(all_rgbs, next_rgb);

  String color_values = display_mode.toString();
  for (int i=0; i < all_rgbs.size(); i++) {
    color_values = color_values + " " + all_rgbs.get(i).toString();
  }

  return color_values;
}

Integer[] getColorValues(int new_color) {
  Integer[] rgb;

  switch(new_color) {
  case 0:
    rgb = new Integer[] {255, 215, 0};
    break;
  case 1:
    rgb = new Integer[] {255, 0, 0};
    break;
  case 2:
    rgb = new Integer[] {0, 255, 0};
    break;
  case 3:
    rgb = new Integer[] {0, 0, 255};
    break;
  case 4:
    rgb = new Integer[] {255, 165, 0};
    break;
  case 5:
    rgb = new Integer[] {34, 139, 34};
    break;
  case 6:
    rgb = new Integer[] {75, 0, 130};
    break;
  default:
    rgb = new Integer[] {25, 25, 112};
    break;
  }

  return rgb;
}

Integer calculateIndividualTransition(Integer single_color, Integer next_color) {
  if (single_color - next_color < 5 && single_color - next_color > -5) single_color = next_color;
  else if (single_color - next_color >= 5) single_color = single_color - 5;
  else if (single_color - next_color <= -5) single_color = single_color + 5;
  return single_color;
}

Integer[] calculateTransition(Integer[] rgb, Integer[] next_rgb) {
  if (next_rgb[0] != rgb[0] || next_rgb[1] != rgb[1] || next_rgb[2] != rgb[2]) {
    for (int i = 0; i < rgb.length; i++) rgb[i] = calculateIndividualTransition(rgb[i], next_rgb[i]);
  }
  return rgb;
}

public static void printServer(Integer which_server, String data)throws InterruptedException {
  // This code starts a thread to ensure that the program doesn't freeze when writing to the clients.
  // Unfortunately, when a client is disconnected abruptly, via dropped wifi signal or unplugging, the
  // Processing server code seems to get stuck in an infinite while loop.  THe only way to avoid this would
  // be to create a new Server library, or do what I did here, which is making sure that the function doesn't hang.
  // If it does hang, the server exits and will be restarted by the bash script that ran this program initially.

  Integer counter = 0;
  final Integer server_to_write_to = which_server;
  final String data_to_write = data;
  Thread thread = new Thread(new Runnable() {
    @Override
      public void run() {
      switch(server_to_write_to) {
      case 1:
        s1.write(data_to_write);
        break;
      case 2:
        s2.write(data_to_write);
        break;
      }
    }
  }
  );
  thread.start();
  long endTimeMillis = System.currentTimeMillis() + 250;
  while (thread.isAlive()) {
    if (System.currentTimeMillis() > endTimeMillis) {
      System.exit(0);
    }
    try {
      Thread.sleep(1);
    }
    catch (InterruptedException t) {
    }
    counter++;
  }
}