import processing.net.*;
import ddf.minim.analysis.*;
import ddf.minim.*;

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
    float volume_adjuster = 0.0; // This is an unused variable, but may be used in future iterations
    int[] range_size = {40, 140, 180, 240, 280, 320, 400, 650, 1250, 1500, 2000, 2000, 2000, 3000, 3000, 3000};
    int range_size_sum = 0;
    for (int i=0; i<range_size.length; i++) {
      spectrum_range_arraylist.add(spectrum_range_arraylist.size(), new SpectrumRange(range_size_sum, range_size_sum + range_size[i]));
      range_size_sum = range_size_sum + range_size[i];
    }
    spectrum_range_arraylist_size = spectrum_range_arraylist.size();
  }

  void processSpectrumData() {
    fft.forward(in.mix);

    for (SpectrumRange sr : spectrum_range_arraylist) {
      sr.calculateAverage(fft);
    }
  }

  Integer calculateAverage() {
    Integer avg_Integer = 0;
    float avg_float = 0.0;
    int total_height = 0;
    for (SpectrumRange sr : spectrum_range_arraylist) {
      total_height = total_height + sr.getHeighttoDisplay();
    }

    avg_float = (float)(total_height / spectrum_range_arraylist_size);

    if (avg_float > 18) {
      volume_adjuster = volume_adjuster + 0.1;
    } else {
      if (avg_float < 0.5) {
        avg_float = 0;
        for (SpectrumRange sr : spectrum_range_arraylist) {
          sr.setHeighttoDisplay(0);
        }
      }
      if (volume_adjuster > 1) {
        volume_adjuster = volume_adjuster - .05;
      }
    }

    avg_Integer = (int)avg_float;

    return avg_Integer;
  }

  String concatenateStringtoSend(Integer total_loop_passes) {
    Integer avg_Integer = calculateAverage();
    String string_to_send = total_loop_passes.toString() + " " + avg_Integer.toString();

    for (SpectrumRange sr : spectrum_range_arraylist) {
      string_to_send = string_to_send + " " + sr.getHeighttoDisplay();
    }

    return string_to_send;
  }

  void stopListing() {
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

  float calculateAverage(FFT fft) {
    float avg = distance_adjustor * fft.calcAvg(lower_range, upper_range);
    double height_to_display_double = Math.pow(avg, .5);
    height_to_display_int = height_to_display_double < 32 ? (int)height_to_display_double : 32;

    return avg;
  }

  void setHeighttoDisplay(int htd) {
    height_to_display_int = htd;
  }

  int getHeighttoDisplay() {
    return height_to_display_int;
  }
}