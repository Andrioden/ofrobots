import random

# noinspection PyMethodMayBeStatic
class CodeRunner:

    def __init__(self, robots):
        self.result = CodeRunFightResult()
        self.robots = robots
        for robot in self.robots:
            # Attributes added to the robot needed to "run code"
            robot.next_instruction_index = 0
            robot.instructions = []
            code_instructions = self._get_instructions_array(robot.code)
            self._store_instructions_to_ram(robot, code_instructions)

    def _store_instructions_to_ram(self, robot, code_instructions):
        memory_lack = robot.memory - len(code_instructions)
        if memory_lack < 0:
            for _ in range(memory_lack*-1):
                code_instructions.pop(random.randint(0,len(code_instructions)-1))
            self.result.logs.append("Warning %s: Insufficient memory for all instructions from code. Dropped some instructions." % robot.name)
        robot.instructions = code_instructions

    def fight(self):
        alive_robots = self.robots
        while self._any_robot_has_energy() and len(alive_robots) > 1:
            # Run second of robot instructions
            a_second_of_instructions = []
            for robot in self.robots:
                try:
                    for ins in self._get_next_robot_instructions(robot):
                        a_second_of_instructions.append({'robot': robot, 'instruction': ins})
                except RobotException as ex:
                    self.result.logs.append("Robot %s crashed: %s" % (robot.name, ex.message))
                    robot.crashed = True

            # Apply all instructions
            for ins in a_second_of_instructions:
                self.result.logs.append("--- %s instruction: %s" % (ins['robot'].name, ins['instruction']))
                if ins['instruction'] == "DO ATTACK":
                    self._robot_attacks_random_robot(ins['robot'])
                else:
                    self.result.logs.append("------ Instruction not understood")
            self.result.logs.append("A second passed. Robot energy status: %s" % ["%s (%s)" % (r.name, r.energy) for r in self.robots])
            alive_robots = self._get_alive_robots()
            if len(alive_robots) == 1:
                self.result.winner = alive_robots[0]
                self.result.logs.append("Robot %s won!" % self.result.winner.name)
        return self.result

    def _robot_attacks_random_robot(self, attacker):
        target = self._get_another_robot(attacker)
        target.health -= attacker.damage
        self.result.logs.append(("Robot %s damaged %s with %s damage so it is now at %s health" % (attacker.name, target.name, attacker.damage, target.health)))

    def _get_another_robot(self, robot):
        robot_indexes = range(len(self.robots))
        random.shuffle(robot_indexes)
        for target_robot_index in robot_indexes:
            if self.robots[target_robot_index] != robot:
                return self.robots[target_robot_index]
        raise Exception("Could not find another robot")

    def _any_robot_has_energy(self):
        for robot in self.robots:
            if robot.crashed:
                continue
            elif robot.energy > 0:
                return True
        return False

    def _get_alive_robots(self):
        return [r for r in self.robots if r.health > 0]

    def _get_next_robot_instructions(self, robot):
        max_instructions = min(robot.energy, robot.IPS)
        next_instructions = []
        for _ in range(max_instructions):
            if robot.next_instruction_index >= len(robot.instructions):
                raise RobotException("Your robot ran out of code")
            else:
                next_instruction = robot.instructions[robot.next_instruction_index]
                if next_instruction == "LOOP END":
                    robot.next_instruction_index = self._find_previous_loopstart(robot.instructions, robot.next_instruction_index)
                else:
                    next_instructions.append(next_instruction)
                    robot.next_instruction_index += 1
                robot.energy -= 1
        return next_instructions

    def _get_instructions_array(self, code):
        """
        :param code: Dirty code that has newlines, spaces and ;
        :return: Array of instructions like "LOOP", "DO ATTACK", "DO BLOCK"
        """
        code = code.replace('\n', '')
        instructions = []
        for dirty_instruction in code.split(';'):
            clean_instruction = dirty_instruction.strip()
            if clean_instruction:
                instructions.append(clean_instruction)
        return instructions

    def _find_previous_loopstart(self, instructions, from_index):
        for i in range(from_index, -1, -1):
            if instructions[i] == "LOOP START":
                return i
        raise RobotException("LOOP START not found for LOOP END at %s" % from_index)


class CodeRunFightResult:

    def __init__(self):
        self.logs = []
        self.winner = None

    def print_logs(self):
        for log in self.logs:
            print log


class RobotException(Exception):
    pass
