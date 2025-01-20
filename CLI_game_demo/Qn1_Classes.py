import random

# Part a: Character & Vehicle Classes

class Character:
    def __init__(self, name, health, position):
        # Initializing protected character's name, health, and position
        self.__name = name
        self.__health = health
        self.__position = position
       
    def get_name(self):
        return self.__name
    

    # Getter and setter for position
    def get_position(self):
        return self.__position
    
    def set_position(self, new_position):
        self.__position = new_position

    def move(self, new_position):
        # Move character to a new position
        self.set_position(new_position)
        print(f"{self.get_name()} is now at location: {self.get_position()}")

    
    # Getter and setter for health
    def get_health(self):
        return self.__health
    
    def set_health(self, health):
        self.__health = max(health, 0)  # Ensuring health does not go below zero
    
    def light_attack(self, target):
        # Perform a light attack, reducing target's health by 12 points
        target.set_health(target.get_health() - 12)
        self.check_health(target)

    def heavy_attack(self, target):
        # Perform a heavy attack, reducing target's health by 20 points
        #print(f"{self._name} performs a heavy attack on {target._name}.")
        target.set_health(target.get_health() - 20)
        self.check_health(target)

    def check_health(self, target):
    # Check if the target's health has dropped to zero or below
        if target.get_health() <= 0:
            print(f"{target.get_name()} has been defeated!")
            
        # Display mission result based on who was defeated
            if "Enemy" in target.get_name():  # Checks if the target's name includes "Enemy"
                print("Mission accomplished!")
                print("<<<<<< The End >>>>>>")
            else:  # Otherwise, assume the hero has been defeated
                print("Mission failed!")
                print("<<<<<< The End >>>>>>")

    def interact(self, object):
        self._object = object
        print(f"{self.get_name()} is interecating with a {self._object}")   

    def display_health(self):
        # Display the character's current health
        print(f"{self.get_name()}'s Health: {self.get_health()}")
        
    def hero_taunt(self):
        # Enemy taunts to hero
        print(f"{self.get_name()}: You can't stop me!")


class Vehicle:
    def __init__(self, type, speed, fuel_level):
        # Initializing protected vehicle type, speed, and fuel level
        self.__type = type
        self.__speed = speed
        self.__fuel_level = fuel_level

    # Getter and setter for fuel level
    def get_fuel_level(self):
        return self.__fuel_level
    
    def set_fuel_level(self, fuel_level):
        self.__fuel_level = fuel_level
        
    def drive(self, fuel_needed):
        # Drive the vehicle if there's enough fuel, reducing fuel by required amount
        if self.get_fuel_level() >= fuel_needed:
            print(f"The {self.get_type()} is driving at {self.__speed} Km/hr.")
            self.set_fuel_level(self.get_fuel_level() - fuel_needed)
            print(f"The {self.get_type()} has {self.get_fuel_level()} fuel left after driving.")
        else:
            # If insufficient fuel
            print(f"The {self.get_type()} doesn't have enough fuel to drive. \nRequired additional fuel is {fuel_needed - self.get_fuel_level()}")

    def refuel(self):
        # Refuel the vehicle to full capacity (100 units)
        self.set_fuel_level(100)
        print(f"The {self.get_type()} is refueled to {self.get_fuel_level()}.")

    def stop(self):
        # Stop the vehicle
        print(f"The {self.get_type()} has stopped.")

    def get_type(self)  -> str:
        # Getting the type of the vehicle 
        return self.__type


# part b: Character Having a Vehicle

class Character_having_aVehicle(Character):
    def get_in(self, vehicle):
        # Character enters the vehicle
        self.vehicle = vehicle
        print(f"{self.get_name()} hopped into the {vehicle.get_type()}.")

    def get_out(self):
        # Character exits the vehicle
        if hasattr(self, '_Character_having_aVehicle__vehicle'):
            print(f"{self.get_name()} rolled out of the {self.__vehicle.get_type()}.")
            del self.__vehicle
        else:
            # If character is not in a vehicle
            print(f"{self.get_name()} is not in a vehicle.")


# Part c: HeroCharacter Class

class HeroCharacter(Character_having_aVehicle):
    # special abilities
    def double_jump(self):
        return f"{self.get_name()} double jumped!"

    def fast_run(self):
        return f"{self.get_name()} is running fast!"


#part d: Enemy Class with Attack Combos

class Enemy(Character):
    def __init__(self, name, health, position):
        # Initialize enemy with a single attack combo
        super().__init__(name, health, position)
        self.combo_list = [["light", "light", "heavy"]]  # Enemy's attack pattern

    def taunt(self):
        # Enemy taunts the hero
        print(f"{self.get_name()}: I won't let you leave!")


# Function to execute combat with combos
def execute_combo(character, target, combo):
    # Execute a combo of attacks for a character against a target
    print(f"\n--- {character.get_name()}'s Combo Turn ---")
    
    # Show health of both characters before executing combo
    print(f"{character.get_name()}'s Health: {character.get_health()}")
    print(f"{target.get_name()}'s Health: {target.get_health()}")
    print(f"{character.get_name()} uses combo: {combo}")

    for attack_type in combo:
        # Perform light or heavy attack based on combo type
        if attack_type == "light":
            character.light_attack(target)
        elif attack_type == "heavy":
            character.heavy_attack(target)
        
        # Break if target's health is zero or less
        if target.get_health() <= 0:
            break



