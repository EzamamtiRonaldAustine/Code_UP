from Qn1_Classes import *

#p;art e Game Scenario 1

def game_scenario_1():

    print("\n***---- Game Scenario 1 ----***")
    hero1 = HeroCharacter("Max", 100, "Safe House")
    enemy = Enemy("Enemy1", 100, "Petrol Station")
    car = Vehicle("BMW", 65, 20)

    hero1.get_in(car)
    print(f"Starting_fuel_level: {car.get_fuel_level()}")
    car.drive(30)  # Car uses 30 units of fuel to drive
    hero1.move("Petrol Station")
    car.stop()
    hero1.get_out()
    print("\n")
    hero1.interact("petrol container")
    car.refuel()  # Car is refueled back to 100

    # Enemy appears and taunts the hero
    enemy.taunt()
    hero1.hero_taunt()

    # Hero's unique combo list
    hero1.combo_list = [
        ["light", "heavy", "light"],
        ["heavy", "light", "heavy"],
        ["light", "light", "heavy", "heavy"]
    ]

    # Alternate attack turns between hero and Enemy until one is defeated
    while hero1.get_health() > 0 and enemy.get_health() > 0:
        hero_combo = random.choice(hero1.combo_list)
        execute_combo(hero1, enemy, hero_combo)

        # Check if the enemy is defeated after Hero's turn
        if enemy.get_health() <= 0:
            break

        # Enemy's turn to attack Hero
        enemy_combo = enemy.combo_list[0]
        execute_combo(enemy, hero1, enemy_combo)


# Game Scenario 2

def game_scenario_2():

    print("\n***---- Game Scenario 2 ----***")
    hero2 = HeroCharacter("Tommy", 50, "Safe House")
    enemy = Enemy("Enemy2", 120, "Petrol Station")
    car = Vehicle("SRT", 80, 30)

    hero2.get_in(car)
    print(f"Starting_fuel_level: {car.get_fuel_level()}")
    car.drive(30)  # Car uses 30 units of fuel to drive
    hero2.move("Petrol Station")
    car.stop()
    hero2.get_out()
    print("\n")
    hero2.interact("petrol container")
    car.refuel()  # Car is refueled back to 100

    # Enemy appears and taunts the hero
    enemy.taunt()
    hero2.hero_taunt()

    # hero's unique combo list
    hero2.combo_list = [
        ["heavy", "heavy", "light"],
        ["light", "light", "heavy"],
        ["light", "heavy", "light", "heavy"]
    ]

    # Alternate attack turns between hero and Enemy until one is defeated
    while hero2.get_health() > 0 and enemy.get_health() > 0:
        hero_combo = random.choice(hero2.combo_list)
        execute_combo(hero2, enemy, hero_combo)

        # Check if the enemy is defeated after Hero's turn
        if enemy.get_health() <= 0:
            break

        # Enemy's turn to attack hero
        enemy_combo = enemy.combo_list[0]
        execute_combo(enemy, hero2, enemy_combo)


# Game Scenario 3

def game_scenario_3():

    print("\n***---- Game Scenario 3 ----***")
    hero3 = HeroCharacter("Jane", 80, "Safe House")
    enemy = Enemy("Enemy3", 50, "Ware House")

    print(f"{hero3.fast_run()}, from the {hero3.get_position()}")
    hero3.move("Ware House")
    hero3.interact("Box")
    print("You have got a new Item")
    
    # Enemy appears and taunts the hero
    enemy.taunt()

    # hero's unique combo list
    # hero3.combo_list = [["light"]]
    
    hero3.combo_list = []
    
    if len(hero3.combo_list) == 0:
            print("Hero: Catch me if you can!")
            print(hero3.double_jump())
            print(hero3.fast_run())
            print(f"{hero3.get_name()} escaped from {enemy.get_name()}.")
            return
            

    # Alternate attack turns between hero and Enemy until one is defeated
    while hero3.get_health() > 0 and enemy.get_health() > 0:
        
        hero_combo = random.choice(hero3.combo_list)
        execute_combo(hero3, enemy, hero_combo)

        # Check if the enemy is defeated after Hero's turn
        if enemy.get_health() <= 0:
            break

        # Enemy's turn to attack hero
        enemy_combo = enemy.combo_list[0]
        execute_combo(enemy, hero3, enemy_combo)

game_scenario_1()
game_scenario_2()
game_scenario_3()
