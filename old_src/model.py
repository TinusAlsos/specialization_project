from dataclasses import dataclass
from battery_storage import BatteryStorage
import numpy as np


def basic_solver(
    battery: BatteryStorage,
    production_curve: np.array,
    electricity_price_curve: np.array,
    dt: float,
    low_price_threshold: float,
    high_price_threshold: float,
):
    """Basic solver for battery storage optimization problem using a threshold-based strategy.

    Args:
        battery (BatteryStorage): Battery storage object
        production_curve (np.array): Array of energy production values (MW)
        electricity_price_curve (np.array): Array of electricity price values (£/MWh)
        dt (float): Time step (hours)
        low_price_threshold (float): Low price threshold (£/MWh)
        high_price_threshold (float): High price threshold (£/MWh)"""

    T = len(production_curve)

    battery_soc = np.zeros(T + 1)
    battery_soc[0] = battery.soc
    sold_energy = np.zeros(T)
    stored_energy = np.zeros(T)

    for t in range(T):
        current_production = production_curve[t]
        # Check if the electricity price is below the low price threshold
        if electricity_price_curve[t] < low_price_threshold:
            potential_energy_to_store = min(
                battery.max_charge_rate_mw * dt, current_production
            )
            if battery_soc[t] + potential_energy_to_store <= battery.capacity_mwh:
                # Charge the battery
                battery_soc[t + 1] = (
                    battery_soc[t]
                    + potential_energy_to_store * battery.charge_efficiency
                )
        # Check if the electricity price is above the high price threshold
        elif electricity_price_curve[t] > high_price_threshold:
            potential_energy_to_sell = min(
                battery.max_discharge_rate_mw * dt, battery_soc[t]
            )
            if battery_soc[t] - potential_energy_to_sell >= 0:
                # Discharge the battery
                battery_soc[t + 1] = (
                    battery_soc[t]
                    - potential_energy_to_sell * battery.discharge_efficiency
                )
                sold_energy[t] = potential_energy_to_sell * battery.discharge_efficiency
        else:
            # No action
            battery_soc[t + 1] = battery_soc[t]

        stored_energy[t] = battery_soc[t + 1] - battery_soc[t]
        sold_energy[t] = current_production - stored_energy[t]
    return stored_energy, sold_energy, battery_soc


@dataclass
class Results:
    battery: BatteryStorage
    stored_energy: np.array
    sold_energy: np.array
    battery_soc: np.array
    electricity_price_curve: np.array
    production_curve: np.array
    dt: float

    def __post_init__(self):
        self.T = len(self.production_curve)
        self.charging_curve, self.discharging_curve = (
            self._calculate_charge_discharge_curves()
        )

    def _calculate_charge_discharge_curves(self):
        charging_curve = np.zeros(self.T)
        discharging_curve = np.zeros(self.T)
        for t in range(1, self.T):
            if self.battery_soc[t] > self.battery_soc[t - 1]:
                charging_curve[t - 1] = self.battery_soc[t] - self.battery_soc[t - 1]
            elif self.battery_soc[t] < self.battery_soc[t - 1]:
                discharging_curve[t - 1] = self.battery_soc[t - 1] - self.battery_soc[t]
        return charging_curve, discharging_curve

    @property
    def revenue_curve(self):
        return self.sold_energy * self.electricity_price_curve

    @property
    def revenue(self):
        return np.sum(self.revenue_curve)

    @property
    def cumulative_charging_curve(self):
        return np.cumsum(self.charging_curve)

    @property
    def cumulative_discharging_curve(self):
        return np.cumsum(self.discharging_curve)

    @property
    def charge_discharge_curve(self):
        return self.charging_curve - self.discharging_curve

    @property
    def cumulative_charge_discharge_curve(self):
        return np.cumsum(self.charge_discharge_curve)

    @property
    def loss_charge_curve(self):
        return (
            (1 - self.battery.charge_efficiency)
            * self.charging_curve
            / self.battery.charge_efficiency
        )

    @property
    def loss_discharge_curve(self):
        return (
            (1 - self.battery.discharge_efficiency)
            * self.discharging_curve
            / self.battery.discharge_efficiency
        )

    @property
    def loss_charge_discharge_curve(self):
        return self.loss_charge_curve + self.loss_discharge_curve

    @property
    def cumulative_loss_charge_curve(self):
        return np.cumsum(self.loss_charge_curve)

    @property
    def cumulative_loss_discharge_curve(self):
        return np.cumsum(self.loss_discharge_curve)

    @property
    def cumulative_loss_charge_discharge_curve(self):
        return np.cumsum(self.loss_charge_discharge_curve)

    @property
    def charge_discharge_loss(self):
        return np.sum(self.loss_charge_discharge_curve)


if __name__ == "__main__":
    # Create a battery storage object
    capacity_mwh = 100
    max_charge_rate_mw = 10
    max_discharge_rate_mw = 10
    charge_efficiency = 0.95
    discharge_efficiency = 0.95
    soc = 0
    battery = BatteryStorage(
        capacity_mwh,
        max_charge_rate_mw,
        max_discharge_rate_mw,
        charge_efficiency,
        discharge_efficiency,
        soc,
    )
    # Print the battery object
    print(battery)
    # Output: BatteryStorage(capacity_mwh=100, max_charge_rate_mw=10, max_discharge_rate_mw=10, charge_efficiency=0.95, discharge_efficiency=0.95, soc=0)
