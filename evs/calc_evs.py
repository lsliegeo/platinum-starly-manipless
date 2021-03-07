from math import floor

table_file = 'ev_table.csv'
route_starts = [(9, 'routes/lvl_9.txt'), (10, 'routes/lvl_10.txt'), (11, 'routes/lvl_11.txt')]
route_file = 'routes/post_mars.txt'
output_file_name = 'route-short.mdr'

debug = False

# {pokemon_name: (exp_yield, [ev_yields])}
data = {}
with open(table_file) as f:
    for line in f:
        line = line.replace('\n', '').split(',')
        name = line[0].lower()
        exp = int(line[1])
        evs = [int(ev) for ev in line[2:8]]
        data[name] = (exp, evs)

# total experience needed in order to reach 'current_lvl'
def total_exp_needed(current_lvl):
    return floor(6 / 5 * current_lvl ** 3 - 15 * current_lvl ** 2 + 100 * current_lvl - 140)

# experience needed in order to level up from 'current_lvl' to 'current_lvl + 1'
def exp_to_next_lvl(current_lvl):
    return total_exp_needed(current_lvl + 1) - total_exp_needed(current_lvl)

# state for managing current lvl, exp and writing evs during level up
class Starly:

    def __init__(self, start_lvl, file):
        self.lvl = start_lvl
        self.exp_remaining = exp_to_next_lvl(self.lvl)
        self.evs = [0, 0, 0, 0, 0, 0]
        self.file = file
        self.opponents = []
        file.write(f'\n{start_lvl}:\n')
        self.print()

    # write evs at the start of current level
    def print(self):
        self.file.write(f'   {self.lvl} -> {", ".join([str(ev) for ev in self.evs])}')
        if self.opponents:
            self.file.write(f' # {", ".join(self.opponents)}')
        self.file.write('\n')

    def check_lvl_up(self):
        if self.exp_remaining <= 0:
            self.lvl += 1
            self.exp_remaining += exp_to_next_lvl(self.lvl)
            self.print()
            self.opponents.clear()
            self.check_lvl_up() # multiple level ups in a row

    # force the current level and throw away any remaining exp, in order to simulate rare candies
    def force(self, target_lvl):
        if debug:
            print(f'forcing from lvl {self.lvl} with {self.exp_remaining} exp remaining to lvl {target_lvl}')
        while self.lvl < target_lvl:
            self.exp_remaining = 0
            self.check_lvl_up()

    # gain exp and evs for a defeated (trainer) pokemon
    def fight(self, other_poke_name, other_poke_lvl, shared=False):
        exp, evs = data[other_poke_name]
        self.exp_remaining -= floor(floor(exp * other_poke_lvl / 7) * 1.5 * (0.5 if shared else 1))
        self.evs = [x + y for x, y in zip(self.evs, evs)]
        self.opponents.append(other_poke_name)
        self.check_lvl_up()

# open main route file
with open(route_file) as file:
    main_route = file.read()

# create output file
with open(output_file_name, 'w') as output_file:

    # write base stats for ranger
    output_file.write(':::tracker{species=Starly baseStats="[[40, 55, 30, 30, 30, 60], [55, 75, 50, 40, 40, 80], [85, 120, 70, 50, 50, 100]]"}')

    # the route has 3 different starts, we do separate calculations for lvl 9, 10 and 11 starly
    for start_lvl, route_file in route_starts:

        if debug:
            print(f'\nlvl {start_lvl} route')

        birb = Starly(start_lvl, output_file)

        with open(route_file) as file:
            route_start = file.read()
        route = route_start + '\n' + main_route
        # print(route)

        for line_ in route.split('\n'):
            # print(line_)
            line = line_

            # skip empty lines ?
            if not line:
                continue

            # trim comments
            if '#' in line:
                line = line[:line.find('#')]

            # split line into words
            line = [part.lower() for part in line.split(' ')]

            # workaround for space in mr. mime
            if line[0][-1] == '.':
                line[0] += ' ' + line[1]
                del line[1]

            # finally we can start parsing lines
            if line[0] == 'force':
                target_lvl = int(line[1])
                birb.force(target_lvl)

            else:
                if line[0] not in data:
                    print(f'invalid line: {line_}')
                    continue

                if debug:

                    # does the heracross cause an extra lvl up for the calvin fight?
                    if line[0] == 'heracross' and line[1] == '25':
                        print(f'before heracross: lvl {birb.lvl} with {birb.exp_remaining} exp remaining')
                        birb.fight(line[0], int(line[1]), line[-1] == 'shared')
                        print(f'after heracross: lvl {birb.lvl} with {birb.exp_remaining} exp remaining')
                    elif line[0] == 'bronzor' and line[1] == '23':
                        print(f'before calvin bronzor: lvl {birb.lvl} with {birb.exp_remaining} exp remaining')
                        birb.fight(line[0], int(line[1]), line[-1] == 'shared')
                        print(f'after calvin bronzor: lvl {birb.lvl} with {birb.exp_remaining} exp remaining')
                    elif line[0] == 'shieldon' and line[1] == '23':
                        print(f'before calvin shieldon: lvl {birb.lvl} with {birb.exp_remaining} exp remaining')
                        birb.fight(line[0], int(line[1]), line[-1] == 'shared')
                        print(f'after calvin shieldon: lvl {birb.lvl} with {birb.exp_remaining} exp remaining')
                    elif line[0] == 'kirlia' and line[1] == '38':
                        print(f'before snow route olivia: lvl {birb.lvl} with {birb.exp_remaining} exp remaining')
                        birb.fight(line[0], int(line[1]), line[-1] == 'shared')

                    else:
                        birb.fight(line[0], int(line[1]), line[-1] == 'shared')

                else:
                    birb.fight(line[0], int(line[1]), line[-1] == 'shared')

    output_file.write(':::')
