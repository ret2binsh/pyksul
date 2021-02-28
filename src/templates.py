c_output = "void $project_name() {\n" +\
        "$body" +\
        "}\n"

c_frame = "\tleds[$led_current] = CRGB($color);\n"
c_clear = "\tfor(int i=0;i<NUM_LEDS;i++)\n\t\tleds[i]=CRGB::Black;\n"
c_show  = "\tFastLED.show();\n" 
