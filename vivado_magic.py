import os
import sys
import tempfile
from IPython.core.magic import Magics, magics_class, line_cell_magic
import pexpect


@magics_class
class VivadoMagic(Magics):
  
  def __init__(self, shell, prefix='/opt/Xilinx', version='2018.2'):
    super(VivadoMagic, self).__init__(shell)
    self._prefix = prefix
    self._version = version
 
  def init(self):
    self._set_paths()
    self.child = pexpect.spawn('vivado -mode tcl', encoding='utf-8')
    self.child.expect('Vivado%', timeout=1800)
    self.child.sendeof()
    print(self.child.before)

  def exit(self):
    self.child.expect(pexpect.EOF)
    self.child.sendline('exit')
    
  def _set_paths(self):
    keys = ['Vivado']
    tool_path = [os.path.join(self._prefix, d, self._version, 'bin') for d in os.listdir(self._prefix) if d in keys]
    os.environ['PATH'] += ':' + ':'.join(tool_path)
    
  def _execute(self, cmd):
    self.child.expect('Vivado%', timeout=1800)
    self.child.sendline(cmd)
    self.child.expect('Vivado%')
    self.child.sendeof()
    print(self.child.after, self.child.before)

    
  @line_cell_magic
  def vivado(self, line, cell=None):
    if cell is None:
      self._execute(line)
    else:
      if line:
        with open(line, 'w') as fp:
          fn = line 
          fp.write(cell)
      else:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tcl', delete=False) as fp:
          fn = fp.name
          fp.write(cell)
      self._execute('source {}'.format(fn))


