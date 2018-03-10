import argparse
#import logging
import os
import signal

from cement.core.controller import CementBaseController, expose
from cement.core.foundation import CementApp
from cement.core.exc import CaughtSignal
from cement.utils.shell import Prompt

from portfoliotool.herolab.reader import PorReader
from portfoliotool.rptools.models.pathfinder import BaseRptokWriter
from portfoliotool.utils.config import portool_default_config


class BaseController(CementBaseController):
    class Meta:
        label = 'base'
        description = 'HeroLab Portfolio Tool'

    @expose(hide=True)
    def default(self):
        self.app.args.print_help()


class RptokController(CementBaseController):
    class Meta:
        description = 'Make rptools.net Tokens'
        label = 'rptok'
        stacked_type = 'nested'
        stacked_on = 'base'

        arguments = [
            (['-v', '--version'],
             {'action': 'store',
              'choices': BaseRptokWriter.rptok_versions,
              'default': BaseRptokWriter.rptok_versions[-1],
              'help': 'Output rptok version'}),
            (['POR_FILE'],
             {'action': 'store',
              'type': argparse.FileType('rb')})
            ]

    @expose(hide=True)
    def default(self):
        portfolio = PorReader(self.app.pargs.POR_FILE)
        for character in portfolio.characters:
            print('Extracted "%s"' % character.name)
            token = character.get_writer('rptok', self.app.pargs.VERSION)

            save_dir = os.getcwd()
            save_name = os.path.join(save_dir, character.name)
            save_file = token.save_name(save_name)
            ask = Prompt('Save as [%s]?' % save_file, default=save_file)
            save_file = ask.prompt()

            save_ok = True
            if os.path.exists(save_file):
                ask = Prompt('Overwrite %s?' % save_file,
                             default='YES',
                             options=['YES', 'no'])
                if ask.prompt() == 'no':
                    save_ok = False

            if save_ok:
                token.save_as(save_file)




class PorTool(CementApp):
    class Meta:
        arguments_override_config = True
        base_controller = 'base'
        config_defaults = portool_default_config
        handlers = [BaseController, RptokController]
        label = 'portool'


def main():
    with PorTool() as app:
        try:
            app.run()
        except CaughtSignal as e:
            if e.signum == signal.SIGINT:
                print('Cancelled')
                app.exit_code = 2
        except UserWarning as e:
            print(e)
            app.exit_code = 1


if __name__ == '__main__':
    main()
