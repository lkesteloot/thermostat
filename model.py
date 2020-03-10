# Model objects.

# A single sample of the state of the system.
class Sample:
    def __init__(self, id, actual_temp, set_temp, heater_on, outside_temp, recorded_at):
        self.id = id;
        self.actual_temp = actual_temp
        self.set_temp = set_temp
        self.heater_on = heater_on
        self.outside_temp = outside_temp
        self.recorded_at = recorded_at

    def to_object(self):
        return {
            "id": self.id,
            "actual_temp": self.actual_temp,
            "set_temp": self.set_temp,
            "heater_on": self.heater_on,
            "outside_temp": self.outside_temp,
            "recorded_at": self.recorded_at,
        }

