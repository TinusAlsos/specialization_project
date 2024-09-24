from dataclasses import dataclass


@dataclass
class BatteryStorage:
    """
    Dataclass representing a battery energy storage system (BESS).
    """

    capacity_mwh: float  # Total capacity of the battery in MWh
    max_charge_rate_mw: float  # Max charging rate in MW
    max_discharge_rate_mw: float  # Max discharging rate in MW
    charge_efficiency: float  # Charging efficiency (typically less than 1)
    discharge_efficiency: float  # Discharging efficiency
    soc: float = 0  # State of Charge (MWh), initialized to 0


if __name__ == "__main__":
    # Create a battery storage object
    battery = BatteryStorage()

    # Print the battery object
    print(battery)
    # Output: BatteryStorage(capacity_mwh=100, max_charge_rate_mw=10, max_discharge_rate_mw=10, charge_efficiency=0.95, discharge_efficiency=0.95, soc=0)
