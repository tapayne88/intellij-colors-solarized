#!env python

import sys
import re
import math
import xml.etree.ElementTree as ET
import argparse

class LightenUp:

    def __init__(self, verbose):
        self.verbose = verbose

    def run(self, saturation, lightness):
        tree = ET.parse('Solarized Dark.icls')
        root = tree.getroot()

        root.set('name', 'Solarized Dark - Modified');

        for option in root.iter('option'):
            self.handleOption(option, saturation, lightness)

        attrs = root.find('attributes')
        for option in attrs.iter('option'):
            self.handleOption(option, saturation, lightness)

        tree.write('Solarized Dark Modified.icls', "UTF-8", True);

    def handleOption(self, option, saturation, lightness):
        value = option.get('value')

        if value is None:
            return

        if re.match('[0-9a-f]{6}', value):
            self._log()
            self._log("Name:", option.get('name'))
            self._log("Original HEX value:", value)

            hsl_value = self.hex_to_hsl(value)
            self._log("Original HSL value:", hsl_value)

            altered_value = self.alter(hsl_value, saturation, lightness)
            self._log("New HSL value:", altered_value)

            new_value = self.hsl_to_hex(altered_value)
            self._log("New HEX value:", new_value)

            option.set('value', new_value)

    def hex_to_hsl(self, value):
        r,g,b = tuple(int(value[i:i+2], 16) for i in range(0, 6, 2))
        return self._rgb_to_hsl(r, g, b)

    def alter(self, value, saturation, lightness):
        val1 = self._inc_value(value[1], saturation)
        val2 = self._inc_value(value[2], lightness)

        return (value[0], val1, val2)

    def hsl_to_hex(self, value):
        r,g,b = self._hsl_to_rgb(value[0], value[1], value[2])

        # Convert the channels' values to hex values.
        r = hex(r)[2:].zfill(2)
        g = hex(g)[2:].zfill(2)
        b = hex(b)[2:].zfill(2)

        return str(r) + str(g) + str(b)

    def _log(self, *args):
        if (self.verbose):
            for arg in args:
                sys.stdout.write(str(arg) + " ")
            sys.stdout.write("\n")

    def _inc_value(self, value, inc):
        if (inc is None):
            return value

        new_val = value + inc
        if (new_val >= 0 and new_val <= 100):
            return new_val
        return value

    def _rgb_to_hsl(self,r,g,b):
        """Converts an rgb(a) value to an hsl(a) value.
        Attributes:
            self: The Regionset object.
            r:    The value of the red channel   (0 - 255)
            g:    The value of the green channel (0 - 255)
            b:    The value of the blue channel  (0 - 255)
            a:    The value of the alpha channel (0.0 - 1.0)
        """

        r = float(r) / 255.0
        g = float(g) / 255.0
        b = float(b) / 255.0

        # Calculate the hsl values.
        cmax = max(r, g, b)
        cmin = min(r, g, b)

        delta = cmax - cmin

        # Hue
        if (cmax == r) and (delta > 0):
            h = 60 * (((g - b) / delta) % 6.0)

        elif (cmax == g) and (delta > 0):
            h = 60 * (((b - r) / delta) + 2.0)

        elif (cmax == b) and (delta > 0):
            h = 60 * (((r - g) / delta) + 4.0)

        elif (delta == 0):
            h = 0

        # Lightness
        l = (cmax + cmin) / 2.0

        # Saturation
        if (delta == 0):
            s = 0

        else:
            s = (delta / (1 - abs((2 * l) - 1)))

        s = s * 100.0
        l = l * 100.0

        return (h, s, l)

    def _hsl_to_rgb(self, h, s, l):
        """Converts an hsl(a) value to an rgb(a) value.
        Attributes:
            self: The Regionset object.
            h:    The value of the hue channel        (0.0 - 360.0)
            s:    The value of the saturation channel (0.0 - 100.0)
            l:    The value of the lightness channel  (0.0 - 100.0)
        """

        h = float(h) / 360
        s = float(s) / 100
        l = float(l) / 100

        # Unsaturated colors have equal rgb channels.
        if s is 0:
            r = l * 255
            g = l * 255
            b = l * 255

        # Magic :)
        else:

            if l < 0.5:
                var_1 = l * (1 + s)

            else:
                var_1 = (l + s) - (l * s)

            var_2 = 2 * l - var_1

            r = 255 * self._hue_to_rgb(var_1, var_2, (h + 0.333))
            g = 255 * self._hue_to_rgb(var_1, var_2, h)
            b = 255 * self._hue_to_rgb(var_1, var_2, (h - 0.333))

        r = int(math.ceil(r))
        g = int(math.ceil(g))
        b = int(math.ceil(b))

        return (r, g, b)

    def _hue_to_rgb(self, v1, v2, vH):
        """Assists with converting hsl to rgb values.
        Attributes:
            self: The Regionset object.
            v1:   The first part of the hsl collection
            v2:   The second part of the hsl collection
            vH:   The thrid part of the hsl collection
        """

        if vH < 0:
            vH += 1

        if vH > 1:
            vH -= 1

        if ((6 * vH) < 1):
            return (v2 + (v1 - v2) * 6 * vH)

        if ((2 * vH) < 1):
            return v1

        if ((3 * vH) < 2):
            return (v2 + (v1 - v2) * ((0.666) - vH) * 6)

        return v2



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s, --saturation", dest="saturation", type=int, help="Alteration to be made to the colour saturations", metavar="+/-<int>")
    parser.add_argument("-l, --lightness", dest="lightness", type=int, help="Alteration to be made to the colour lightness", metavar="+/-<int>")
    parser.add_argument("-v, --verbose", dest="verbose", action="store_true", help="Verbose mode")

    args = parser.parse_args()

    saturation = args.saturation
    lightness = args.lightness
    verbose = args.verbose

    if (saturation is not None or lightness is not None):
        lu = LightenUp(verbose)
        lu.run(saturation, lightness)
    else:
        print "Missing actions, see help"
        parser.print_help()

if __name__ == '__main__':
    main()
