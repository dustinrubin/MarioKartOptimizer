import csv
import re
from enum import Enum
from collections import namedtuple
from io import StringIO
import matplotlib.pyplot as plt

#https://docs.google.com/spreadsheets/d/1g7A-38tn9UAIbB2B3sZI-MpILsS3ZS870UTVMRRxh4Q/edit#gid=0
#https://docs.google.com/spreadsheets/d/1GD-bAZTwvlYLhkcSBl9tUuOwFfssGhBkXwP4Vur_fXc/edit#gid=0
#https://www.youtube.com/watch?v=xo-Qt2mkjQs

class PartType(Enum):
    BODIES = 1
    TIRES = 2
    GLIDER = 3
    CHARACTER = 4

KartPart = namedtuple("KartPart", "part_type name land_speed anti_gravity_speed water_speed gliding_speed acceleration weight land_handling anti_gravity_handling water_handling gliding_handling traction mini_turbo invincibility")

def convertBarToValue(value):
    return value * 4 - 3

def read_kart_parts(file_name, part_type, use_value_form=False):
    body = []

    with open(file_name, "r") as file:
        data = file.read()
        modified_data = StringIO(data)
        csv_reader = csv.reader(modified_data)
        for row in csv_reader:
            if use_value_form:
                row = [row[0]] + [convertBarToValue(float(value)) for value in row[1:]]
            part = KartPart(
                part_type=part_type,
                name=row[0],
                land_speed=float(row[1]),
                anti_gravity_speed=float(row[2]),
                water_speed=float(row[3]),
                gliding_speed=float(row[4]),
                acceleration=float(row[5]),
                weight=float(row[6]),
                land_handling=float(row[7]),
                anti_gravity_handling=float(row[8]),
                water_handling=float(row[9]),
                gliding_handling=float(row[10]),
                traction=float(row[11]),
                mini_turbo=float(row[12]),
                invincibility=float(row[13])
            )
            body.append(part)
    return body

# Call the function and save the return value in 'body'
body = read_kart_parts("karts.csv", PartType.BODIES)
tires = read_kart_parts("tires.csv", PartType.TIRES)
glider = read_kart_parts("glider.csv", PartType.GLIDER)
characters = read_kart_parts("characterIsabelle.csv", PartType.CHARACTER)


builds = []

for b in body:
    for t in tires:
        for g in glider:
            for c in characters:
                build = KartPart(
                    part_type=None,
                    name=f"{c.name} - {b.name} - {t.name} - {g.name}",
                    land_speed=b.land_speed + t.land_speed + g.land_speed + c.land_speed,
                    anti_gravity_speed=b.anti_gravity_speed + t.anti_gravity_speed + g.anti_gravity_speed + c.anti_gravity_speed,
                    water_speed=b.water_speed + t.water_speed + g.water_speed + c.water_speed,
                    gliding_speed=b.gliding_speed + t.gliding_speed + g.gliding_speed + c.gliding_speed,
                    acceleration=b.acceleration + t.acceleration + g.acceleration + c.acceleration,
                    weight=b.weight + t.weight + g.weight + c.weight,
                    land_handling=b.land_handling + t.land_handling + g.land_handling + c.land_handling,
                    anti_gravity_handling=b.anti_gravity_handling + t.anti_gravity_handling + g.anti_gravity_handling + c.anti_gravity_handling,
                    water_handling=b.water_handling + t.water_handling + g.water_handling + c.water_handling,
                    gliding_handling=b.gliding_handling + t.gliding_handling + g.gliding_handling + c.gliding_handling,
                    traction=b.traction + t.traction + g.traction + c.traction,
                    mini_turbo=b.mini_turbo + t.mini_turbo + g.mini_turbo + c.mini_turbo,
                    invincibility=b.invincibility + t.invincibility + g.invincibility + c.invincibility
                )
                builds.append(build)




def is_pareto_optimal(build1, build2, attr1, attr2):
    better_or_equal = getattr(build1, attr1) >= getattr(build2, attr1) and getattr(build1, attr2) >= getattr(build2, attr2)
    strictly_better = getattr(build1, attr1) > getattr(build2, attr1) or getattr(build1, attr2) > getattr(build2, attr2)
    return better_or_equal and strictly_better

def find_pareto_optimal_builds(builds, attr1, attr2):
    pareto_optimal_builds = []

    for candidate in builds:
        is_pareto_optimal_build = True
        for other in builds:
            if is_pareto_optimal(other, candidate, attr1, attr2):
                is_pareto_optimal_build = False
                break

        if is_pareto_optimal_build:
            pareto_optimal_builds.append(candidate)

    return pareto_optimal_builds





def is_strictly_dominated(build1, build2, attributes):
    strictly_worse = all(getattr(build1, attr) <= getattr(build2, attr) for attr in attributes)
    worse_in_some = any(getattr(build1, attr) < getattr(build2, attr) for attr in attributes)
    return strictly_worse and worse_in_some

def remove_dominated_builds(builds):
    all_attributes = ['land_speed', 'anti_gravity_speed', 'water_speed', 'gliding_speed',
                      'acceleration', 'weight', 'land_handling', 'anti_gravity_handling',
                      'water_handling', 'gliding_handling', 'traction', 'mini_turbo', 'invincibility']

    non_dominated_builds = []
    for build in builds:
        is_dominated = False
        for other_build in builds:
            if build != other_build and is_strictly_dominated(build, other_build, all_attributes):
                is_dominated = True
                break

        if not is_dominated:
            non_dominated_builds.append(build)

    return non_dominated_builds



def plot_pareto_frontier(builds, attr1, attr2):
    plt.figure(figsize=(10, 6))
    plt.title("Pareto Frontier")
    plt.xlabel(attr1)
    plt.ylabel(attr2)

    x = [getattr(build, attr1) for build in builds]
    y = [getattr(build, attr2) for build in builds]

    plt.scatter(x, y)

    # Display the text labels (names) and the exact numbers on the graph
    for i, build in enumerate(builds):
        plt.annotate(build.name, (x[i], y[i]), textcoords="offset points", xytext=(0, -15), ha='center', fontsize=8)
        plt.annotate(f"({x[i]}, {y[i]})", (x[i], y[i]), textcoords="offset points", xytext=(0, 5), ha='center', fontsize=8)

    plt.show()


def select_builds_with_priority(builds, attr1, attr2, ordered_list):
    build_groups = {}
    selected_builds = []

    # Group builds with identical attr1 and attr2
    for build in builds:
        key = (getattr(build, attr1), getattr(build, attr2))
        if key not in build_groups:
            build_groups[key] = [build]
        else:
            build_groups[key].append(build)

    # Iterate over ordered_list and eliminate builds with lower values
    for group in build_groups.values():
        for attr in ordered_list:
            max_value = max(getattr(build, attr) for build in group)
            group = [build for build in group if getattr(build, attr) == max_value]

            # If only one build is left or all builds are perfectly tied, stop the loop
            if len(group) == 1 or all(getattr(build, attr) == max_value for build in group for attr in ordered_list):
                break

        selected_builds.append(group[0])

    return selected_builds



attribute1='land_speed'
attribute2='mini_turbo'
print("Number of builds",len(builds))
pareto_optimal_builds = find_pareto_optimal_builds(builds, 'land_speed', 'mini_turbo')
print("Number of pareto_optimal_builds",len(pareto_optimal_builds))
non_dominated_builds = remove_dominated_builds(pareto_optimal_builds)
ordered_list = ['acceleration', 'anti_gravity_speed', 'land_handling', 'gliding_speed', 'water_speed', 'anti_gravity_handling', 'water_handling', 'gliding_handling', 'traction', 'weight', 'invincibility']
print("Number of non dominated builds",len(non_dominated_builds))
print(non_dominated_builds)
selected_builds = select_builds_with_priority(non_dominated_builds, attribute1, attribute2, ordered_list)
print("New algorithm number of builds", len(selected_builds))
plot_pareto_frontier(selected_builds, attribute1, attribute2)

def find_specific_build(builds, kart_body, tire, character, glider):
    search_string = f"{character} - {kart_body} - {tire} - {glider}"
    
    for build in builds:
        if build.name == search_string:
            return build
    return None

print(find_specific_build(builds, "Cat_Cruiser", "Button", "Waluigi", "Cloud_Glider"))
# print(find_specific_build(builds, "300_SL_Roadster", "GLA_Tires", "Waluigi", "Cloud_Glider"))
print(find_specific_build(builds, "300_SL_Roadster", "GLA_Tires", "Peach", "Super_Glider"))

# KartPart(part_type=None, name='Waluigi - Cat_Cruiser - Button - Cloud_Glider', land_speed=3.75, anti_gravity_speed=4.5, water_speed=4.25, gliding_speed=4.75, acceleration=4.0, weight=3.25, land_handling=3.25, anti_gravity_handling=3.25, water_handling=2.5, gliding_handling=3.25, traction=2.5, mini_turbo=4.25, invincibility=2.25)
# KartPart(part_type=None, name='Waluigi - 300_SL_Roadster - GLA_Tires - Cloud_Glider', land_speed=4.25, anti_gravity_speed=4.5, water_speed=4.75, gliding_speed=4.75, acceleration=3.5, weight=3.75, land_handling=3.0, anti_gravity_handling=3.0, water_handling=2.5, gliding_handling=3.25, traction=3.0, mini_turbo=3.75, invincibility=3.0)
