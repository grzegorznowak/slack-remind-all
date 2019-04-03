from duckling import DucklingWrapper


class DucklingWrapperMod(DucklingWrapper):
    def parse_time(self, input_str, reference_time=''):
        return super().parse_time(input_str.replace("midday", "noon"), reference_time)
