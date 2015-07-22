# Inspired by https://cloud.google.com/appengine/docs/python/tools/localunittesting

# Correct path so ndb can be imported (in models.py)
import sys
sys.path.insert(0, "C:\Program Files (x86)\Google\google_appengine")
import dev_appserver
dev_appserver.fix_sys_path()

import unittest
from models import Robot
from coderunner import CodeRunner, RobotException


class CodeRunnerTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_instructions_array_simple(self):
        dirty_code = """
            LOOP START;
                DO ATTACK;
        """
        code_runner = CodeRunner([])
        cleaned_code_array = code_runner._get_instructions_array(dirty_code)
        self.assertEqual(['LOOP START', 'DO ATTACK'], cleaned_code_array)

    def test_get_instructions_array_simple2(self):
        dirty_code = """
            LOOP START;

                DO ATTACK;
                DO ATTACK;
                DO BLOCK;

            LOOP END;
        """
        code_runner = CodeRunner([])
        cleaned_code_array = code_runner._get_instructions_array(dirty_code)
        self.assertEqual(['LOOP START', 'DO ATTACK', 'DO ATTACK', 'DO BLOCK', 'LOOP END'], cleaned_code_array)

    def test_find_previous_loopstart1(self):
        instructions = ['LOOP START', 'DO ATTACK', 'DO ATTACK', 'LOOP END']
        code_runner = CodeRunner([])
        prev_loopstart = code_runner._find_previous_loopstart(instructions, 3)
        self.assertEqual(0, prev_loopstart)

    def test_find_previous_loopstart2(self):
        instructions = ['DO ATTACK', 'LOOP START', 'DO ATTACK', 'DO ATTACK', 'LOOP END']
        code_runner = CodeRunner([])
        prev_loopstart = code_runner._find_previous_loopstart(instructions, 3)
        self.assertEqual(1, prev_loopstart)

    def test_find_previous_loopstart_exception(self):
        instructions = ['DO ATTACK', 'DO ATTACK', 'DO ATTACK', 'LOOP END']
        code_runner = CodeRunner([])
        with self.assertRaises(RobotException) as context:
            code_runner._find_previous_loopstart(instructions, 3)
        self.assertTrue("LOOP START not found for LOOP END at 3" in context.exception)


class RobotFightTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_crash(self):
        attack_code = """
            DO ATTACK;
            DO ATTACK;
        """
        r1 = Robot(name="AndriodRobot", damage=1, max_health=6, health=6, code=attack_code, energy=10, IPS=1, memory=2)
        r2 = Robot(name="NelichRobot", damage=1, max_health=6, health=6, code=attack_code, energy=10, IPS=1, memory=2)
        code_runner = CodeRunner([r1, r2])
        result = code_runner.fight()
        self.assertIn("Robot AndriodRobot crashed: Your robot ran out of code", result.logs)

    def test_to_much_code(self):
        attack_code = """
            DO ATTACK;
            DO ATTACK;
        """
        r1 = Robot(name="AndriodRobot", damage=1, max_health=6, health=6, code=attack_code, energy=10, IPS=1, memory=1)
        r2 = Robot(name="NelichRobot", damage=1, max_health=6, health=6, code=attack_code, energy=10, IPS=1, memory=2)
        code_runner = CodeRunner([r1, r2])
        result = code_runner.fight()
        self.assertIn("Warning AndriodRobot: Insufficient memory for all instructions from code. Dropped some instructions.", result.logs)
        self.assertEquals(1, len(r1.instructions))

    def test_bugged_code(self):
        attack_code = """
            DO ATTACKlol;
            DO ATTACK;
        """
        r1 = Robot(name="AndriodRobot", damage=1, max_health=6, health=6, code=attack_code, energy=10, IPS=1, memory=2)
        r2 = Robot(name="NelichRobot", damage=1, max_health=6, health=6, code=attack_code, energy=10, IPS=1, memory=2)
        code_runner = CodeRunner([r1, r2])
        result = code_runner.fight()
        result.print_logs()

    def test_basic_fight(self):
        attack_code = """
            DO ATTACK;
            DO ATTACK;
        """
        r1 = Robot(name="AndriodRobot", damage=1, max_health=6, health=6, code=attack_code, energy=10, IPS=1, memory=2)
        r2 = Robot(name="NelichRobot", damage=1, max_health=6, health=6, code=attack_code, energy=10, IPS=1, memory=2)
        code_runner = CodeRunner([r1, r2])
        result = code_runner.fight()
        self.assertEqual(4, r1.health)
        self.assertEqual(4, r2.health)
        self.assertEqual(8, r1.energy)
        self.assertEqual(8, r2.energy)

    def test_loop_fight(self):
        attack_code = """
            LOOP START;
                DO ATTACK;
            LOOP END;
        """
        r1 = Robot(name="AndriodRobot", damage=2, max_health=6, health=6, code=attack_code, energy=10, IPS=1, memory=3)
        r2 = Robot(name="NelichRobot", damage=3, max_health=6, health=6, code=attack_code, energy=10, IPS=1, memory=3)
        code_runner = CodeRunner([r1, r2])
        result = code_runner.fight()
        self.assertEqual(0, r1.health)
        self.assertEqual(2, r2.health)
        self.assertEqual(5, r1.energy)
        self.assertEqual(5, r2.energy)
        self.assertEqual(r2.name, result.winner.name)

    def test_loop_fight_ips_advantage(self):
        attack_code = """
            LOOP START;
                DO ATTACK;
            LOOP END;
        """
        r1 = Robot(name="AndriodRobot", damage=2, max_health=6, health=6, code=attack_code, energy=10, IPS=2, memory=3)
        r2 = Robot(name="NelichRobot", damage=2, max_health=6, health=6, code=attack_code, energy=10, IPS=1, memory=3)
        code_runner = CodeRunner([r1, r2])
        result = code_runner.fight()
        self.assertEqual(4, r1.health)
        self.assertEqual(0, r2.health)
        self.assertEqual(2, r1.energy)
        self.assertEqual(6, r2.energy)
        self.assertEqual(r1.name, result.winner.name)


if __name__ == '__main__':
    unittest.main()