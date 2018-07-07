import java.io.BufferedReader;
import java.io.FileReader;
import java.io.FileNotFoundException;

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

  String[] getDisplayModes() {
    return display_modes;
  }

  Integer getDisplayModeDuration() {
    return display_mode_duration;
  }
  
  Integer[] getDisplayModeTimer() {
    return display_mode_individual_timer_array;
  }
}