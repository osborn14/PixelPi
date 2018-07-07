import java.io.BufferedReader;
import java.io.FileReader;
import java.io.FileNotFoundException;

class Settings {
  String[] DISPLAY_MODES;
  Integer DISPLAY_MODE_DURATION;
  Integer[] DISPLAY_MODE_INDIVIDUAL_TIMER_ARRAY;

  Settings() {
    BufferedReader br = null;

    String settings_text_file = "server_settings.txt";
    String line = "";
    String split_line_by = ":";

    try {
      br = new BufferedReader(new FileReader(settings_text_file));
      while ((line = br.readLine()) != null) {
        String[] settings_line_segment = line.split(split_line_by);
        String identifier = settings_line_segment[0];
        String value = settings_line_segment[1];
        value = value.replaceAll("\\s", "");

        switch(identifier) {
        case "Display Mode":
          DISPLAY_MODES = value.split(",");
          break;

        case "Display Mode Duration":
          DISPLAY_MODE_DURATION = Integer.parseInt(value);
          break;

        case "Display Mode Timer":
          DISPLAY_MODE_INDIVIDUAL_TIMER_ARRAY = convertCommaStringToIntegerArray(value);
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
    return DISPLAY_MODES;
  }

  Integer getDisplayModeDuration() {
    return DISPLAY_MODE_DURATION;
  }
  
  Integer[] getDisplayModeTimer() {
    return DISPLAY_MODE_INDIVIDUAL_TIMER_ARRAY;
  }
}