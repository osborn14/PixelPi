import processing.core.*; 
import processing.data.*; 
import processing.event.*; 
import processing.opengl.*; 

import processing.net.*; 
import java.util.Random; 
import java.util.Collections; 
import java.io.BufferedReader; 
import java.io.FileReader; 
import java.io.FileNotFoundException; 
import processing.net.*; 
import ddf.minim.analysis.*; 
import ddf.minim.*; 

import java.util.HashMap; 
import java.util.ArrayList; 
import java.io.File; 
import java.io.BufferedReader; 
import java.io.PrintWriter; 
import java.io.InputStream; 
import java.io.OutputStream; 
import java.io.IOException; 

public class ProcessingSpectrumAnalyzer extends PApplet {





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

public void setup() {
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

public void draw() {
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


public void stop() {
  // always close Minim audio classes when you finish with them
  spectrum.stopListing();
  s1.stop();
  s2.stop();
  super.stop();
}

//Integer[] getDisplayMode(){

//}

public String getStringtoPrint(Integer display_mode, Integer[] current_rgb, Integer[] next_rgb) {
  ArrayList<Integer> all_rgbs = new ArrayList();
  Collections.addAll(all_rgbs, current_rgb);
  Collections.addAll(all_rgbs, next_rgb);

  String color_values = display_mode.toString();
  for (int i=0; i < all_rgbs.size(); i++) {
    color_values = color_values + " " + all_rgbs.get(i).toString();
  }

  return color_values;
}

public Integer[] getColorValues(int new_color) {
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

public Integer calculateIndividualTransition(Integer single_color, Integer next_color) {
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

public Integer[] calculateTransition(Integer[] current_rgb, Integer[] next_rgb) {
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


class Rainbow {
  private Integer[] rgb_array = {254, 0, 0};
  private Integer counter, decreasing_color, increasing_color, color_multiplier;

  Rainbow(int cm) {
    counter = 0;
    decreasing_color = 0;
    increasing_color = 0;
    color_multiplier = cm;
  }

  public Integer[] getNextColor() {
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

  public void clearVariables() {
    rgb_array = new Integer[] {254, 0, 0};
    counter = 0;
    decreasing_color = 0;
    increasing_color = 0;
  }
}




class Settings {
  String[] display_modes;
  Integer display_mode_duration;
  Integer[] display_mode_individual_timer_array;

  Settings() {
    BufferedReader br = null;

    String settings_text_file = "server_settings.txt";
    String line = "";
    String split_line_by = ":";
    
    // Set some default values
    display_modes = new String[]{"0", "1", "2", "3"};
    display_mode_duration = 30;
    display_mode_individual_timer_array = new Integer[]{9, 3, 3, 6};
    
    
    try {
      System.out.println("Working Directory = " +
              System.getProperty("user.dir"));
      br = new BufferedReader(new FileReader(settings_text_file));
      while ((line = br.readLine()) != null) {
        String[] settings_line_segment = line.split(split_line_by);
        String identifier = settings_line_segment[0];
        String value = settings_line_segment[1];
        value = value.replaceAll("\\s", "");

        switch(identifier) {
        case "Display Mode":
          display_modes = value.split(",");
          break;

        case "Display Mode Duration":
          display_mode_duration = Integer.parseInt(value);
          break;

        case "Display Mode Timer":
          display_mode_individual_timer_array = convertCommaStringToIntegerArray(value);
          print(display_mode_individual_timer_array);
          break;
        }
      }
    }
    catch (FileNotFoundException e) {
      e.printStackTrace();
    } 
    catch (IOException e) {
      e.printStackTrace();
    } 
    finally {
      if (br != null) {
        try {
          br.close();
        } 
        catch (IOException e) {
          e.printStackTrace();
        }
      }
    }
  }
  private Integer[] convertCommaStringToIntegerArray(String comma_string) {
    String[] string_array = comma_string.split(",");
    Integer[] clean_integer_array = new Integer[string_array.length];

    for (int i = 0; i < string_array.length; i++) {
      clean_integer_array[i] = Integer.parseInt(string_array[i]);
    }

    return clean_integer_array;
  }

  public String[] getDisplayModes() {
    return display_modes;
  }

  public Integer getDisplayModeDuration() {
    return display_mode_duration;
  }
  
  public Integer[] getDisplayModeTimer() {
    return display_mode_individual_timer_array;
  }
}




class Spectrum {
  private ArrayList<SpectrumRange> spectrum_range_arraylist;
  private float volume_adjuster;
  private int spectrum_range_arraylist_size;
  //private String string_to_send = "";
  private Minim minim;
  private AudioInput in;
  private FFT fft;

  Spectrum() {
    int buffer_size = 1024;
    int sample_rate = 44100;
    minim = new Minim(this);

    in = minim.getLineIn(Minim.MONO, buffer_size, sample_rate);
    fft = new FFT(in.bufferSize(), in.sampleRate());
    fft.window(FFT.HAMMING);

    spectrum_range_arraylist = new ArrayList<SpectrumRange>();
    float volume_adjuster = 0.0f; // This is an unused variable, but may be used in future iterations
    int[] range_size = {40, 140, 180, 240, 280, 320, 400, 650, 1250, 1500, 2000, 2000, 2000, 3000, 3000, 3000};
    int range_size_sum = 0;
    for (int i=0; i<range_size.length; i++) {
      spectrum_range_arraylist.add(spectrum_range_arraylist.size(), new SpectrumRange(range_size_sum, range_size_sum + range_size[i]));
      range_size_sum = range_size_sum + range_size[i];
    }
    spectrum_range_arraylist_size = spectrum_range_arraylist.size();
  }

  public void processSpectrumData() {
    fft.forward(in.mix);

    for (SpectrumRange sr : spectrum_range_arraylist) {
      sr.calculateAverage(fft);
    }
  }

  public Integer calculateAverage() {
    Integer avg_Integer = 0;
    float avg_float = 0.0f;
    int total_height = 0;
    for (SpectrumRange sr : spectrum_range_arraylist) {
      total_height = total_height + sr.getHeighttoDisplay();
    }

    avg_float = (float)(total_height / spectrum_range_arraylist_size);

    if (avg_float > 18) {
      volume_adjuster = volume_adjuster + 0.1f;
    } else {
      if (avg_float < 0.5f) {
        avg_float = 0;
        for (SpectrumRange sr : spectrum_range_arraylist) {
          sr.setHeighttoDisplay(0);
        }
      }
      if (volume_adjuster > 1) {
        volume_adjuster = volume_adjuster - .05f;
      }
    }

    avg_Integer = (int)avg_float;

    return avg_Integer;
  }

  public String concatenateStringtoSend(Integer total_loop_passes) {
    Integer avg_Integer = calculateAverage();
    String string_to_send = total_loop_passes.toString() + " " + avg_Integer.toString();

    for (SpectrumRange sr : spectrum_range_arraylist) {
      string_to_send = string_to_send + " " + sr.getHeighttoDisplay();
    }

    return string_to_send;
  }

  public void stopListing() {
    in.close();
    minim.stop();
  }
}

class SpectrumRange {
  private int distance_adjustor_constant, height_to_display_int;
  private float lower_range, upper_range, distance_adjustor;

  SpectrumRange(float lr, float ur) {
    distance_adjustor_constant = 20;

    lower_range = lr;
    upper_range = ur;
    distance_adjustor = (upper_range - lower_range) / distance_adjustor_constant;
  }

  public float calculateAverage(FFT fft) {
    float avg = distance_adjustor * fft.calcAvg(lower_range, upper_range);
    double height_to_display_double = Math.pow(avg, .5f);
    height_to_display_int = height_to_display_double < 32 ? (int)height_to_display_double : 32;

    return avg;
  }

  public void setHeighttoDisplay(int htd) {
    height_to_display_int = htd;
  }

  public int getHeighttoDisplay() {
    return height_to_display_int;
  }
}
  static public void main(String[] passedArgs) {
    String[] appletArgs = new String[] { "ProcessingSpectrumAnalyzer" };
    if (passedArgs != null) {
      PApplet.main(concat(appletArgs, passedArgs));
    } else {
      PApplet.main(appletArgs);
    }
  }
}
