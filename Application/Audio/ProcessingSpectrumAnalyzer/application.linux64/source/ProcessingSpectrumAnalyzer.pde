import processing.net.*;
import java.util.Random;
import java.util.Collections;

static Server s1, s2;
Settings settings;
Random rand;
Spectrum spectrum;
DisplayMode dm;

Rainbow rainbow = new Rainbow(1);

String color_values;

Integer[] main_rgb_to_print, second_rgb_to_print, next_main_rgb_to_print, next_second_rgb_to_print;
int FPS, n1, n2, total_loop_passes;

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
  dm = new DisplayMode(settings);

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

  if (dm.every_loop_counter >= dm.duration * FPS) {
    dm.every_loop_counter = 0;
    //println(dm.current_mode + " --- " + dm.duration_counter + " -- " + dm.individual_timer_array[dm.position]);
    //println(dm.position);


    if (dm.duration_counter > dm.individual_timer_array[dm.position]) {
      if (dm.position < dm.modes.length - 1) {
        dm.position++;
      } else {
        if (dm.current_mode == 1){
          rainbow.clearVariables();
        }
        dm.position = 0;
      }

      //println(dm.position + " ");

      dm.current_mode = Integer.parseInt(dm.modes[dm.position]);
      dm.duration_counter = 0;
    }

    if (dm.current_mode == 0 || dm.current_mode == 2 || dm.current_mode == 3) {
      n1 = rand.nextInt(8);
      n2 = rand.nextInt(8);
      next_main_rgb_to_print = getColorValues(n1);
      next_second_rgb_to_print = getColorValues(n2);
      
      //print(dm.current_mode);
      //print("  ");
      //print(next_main_rgb_to_print[0], next_main_rgb_to_print[1], next_main_rgb_to_print[2]);
      //print(" --- ");
      //println(main_rgb_to_print[0], main_rgb_to_print[1], main_rgb_to_print[2]);
      //println(next_second_rgb_to_print.toString() + " -- " + second_rgb_to_print.toString());
    }

    dm.duration_counter++;
  } else {
    dm.every_loop_counter++;
  }

  //println("Next ---> " + getStringtoPrint(dm.current_mode, next_main_rgb_to_print, next_second_rgb_to_print));

  // THIS CAUSES ERRORS
  if (dm.current_mode == 0 || dm.current_mode == 2 || dm.current_mode == 3) {
    //print(dm.current_mode);
    //  print("           ");
    //  print(main_rgb_to_print[0], main_rgb_to_print[1], main_rgb_to_print[2]);
    
    //print(" --- ");
    //println(next_main_rgb_to_print[0], next_main_rgb_to_print[1], next_main_rgb_to_print[2]);
    
    
    main_rgb_to_print = calculateTransition(main_rgb_to_print, next_main_rgb_to_print);
    //main_rgb_to_print = new Integer[]{128, 128, 128};
    //print("After  -->  ");
    //println(main_rgb_to_print[0], main_rgb_to_print[1], main_rgb_to_print[2]);
    second_rgb_to_print = calculateTransition(second_rgb_to_print, next_second_rgb_to_print);
    color_values = getStringtoPrint(dm.current_mode, main_rgb_to_print, second_rgb_to_print);
  } else if (dm.current_mode == 1) {
    Integer [] main_rgb = rainbow.getNextColor();
    //print("After  -->  ");
    //println(main_rgb_to_print[0], main_rgb_to_print[1], main_rgb_to_print[2]);
    Integer [] second_rgb = main_rgb;
    color_values = getStringtoPrint(dm.current_mode, main_rgb, second_rgb);
  }
  
  //println("Cur ----> " + color_values);
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
  //println("CIT ");
  //if (single_color - next_color < 5 && single_color - next_color > -5) single_color = next_color;
  if (single_color - next_color >= 5) single_color = single_color - 5;
  else if (single_color - next_color <= -5) single_color = single_color + 5;
  else{
    single_color = next_color;
    //print(single_color);
    //print(" and ");
    //print(next_color);
    //println(" are the same!");
  }

  //print("CIT ");
  //print(single_color);
  //print("  ");
  //println(next_color);
  return single_color;
}

Integer[] calculateTransition(Integer[] current_rgb, Integer[] next_rgb) {
  if (next_rgb[0] != current_rgb[0] || next_rgb[1] != current_rgb[1] || next_rgb[2] != current_rgb[2]) {
    //println("true");
    for (int i = 0; i < current_rgb.length; i++) current_rgb[i] = calculateIndividualTransition(current_rgb[i], next_rgb[i]);
  }
  return current_rgb;
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

class DisplayMode {
  String[] modes;
  Integer[] individual_timer_array;
  Integer current_mode, position, duration;
  int every_loop_counter, duration_counter;

  public DisplayMode(Settings settings) {
    every_loop_counter = 0;
    position = 0;
    current_mode = 0;
    duration_counter = 1;
    modes = settings.getDisplayModes();
    duration = settings.getDisplayModeDuration();
    individual_timer_array = settings.getDisplayModeTimer();
  }

  //public Integer getDisplayMode() {
  //}
}