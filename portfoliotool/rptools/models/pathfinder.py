from portfoliotool.rptools.writer import BaseRptokWriter

hack_path = '/Users/siege/Workspace/portfoliotool/portfoliotool/rptools/macros'


class AllyWriter(BaseRptokWriter):
    def _configure(self):
        self.add_macros(hack_path + '/basic/dice.ini')
        self.add_macros(hack_path + '/basic/functions.ini')
        # self.add_macros(hack_path + '/basic/init.ini')
        self.add_macros(hack_path + '/pathfinder/attacks.ini')
        self.add_macros(hack_path + '/pathfinder/character.ini')
        self.add_macros(hack_path + '/pathfinder/options.ini')
        self.add_macros(hack_path + '/pathfinder/spells.ini')


class EnemyWriter(AllyWriter):
    pass
