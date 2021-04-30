from ipykernel.kernelbase import Kernel
import pexpect

class ElmWrapper(object):
    """Wrapper for Elm REPL.
    """
    def __init__(self):

        self.child = pexpect.spawn("elm repl", echo=False, encoding='utf-8')

        self.prompt = "> "
        self.continuation_prompt = "| "
        self._expect_prompt()

    def _expect_prompt(self, timeout=-1, async_=False):
        return self.child.expect_exact([self.prompt, self.continuation_prompt],
                                       timeout=timeout, async_=async_)

    def run_command(self, command, timeout=-1):
        """Send a command to the REPL, wait for and return output.

        :param str command: The command to send. Trailing newlines are not needed.
          This should be a complete block of input that will trigger execution;
          if a continuation prompt is found after sending input, :exc:`ValueError`
          will be raised.
        :param int timeout: How long to wait for the next prompt. -1 means the
          default from the :class:`pexpect.spawn` object (default 30 seconds).
          None means to wait indefinitely.
        """
        # Split up multiline commands and feed them in bit-by-bit
        cmdlines = command.splitlines()
        # splitlines ignores trailing newlines - add it back in manually
        if command.endswith('\n'):
            cmdlines.append('') # empty line at end
        if not cmdlines:
            raise ValueError("No command was given")

        res = []
        self.child.sendline(cmdlines[0])
        # res.append("{") do not show prompt
        # res.append(self.child.after)
        # res.append("}")        
        for line in cmdlines[1:]:
            prompt = self._expect_prompt(timeout=timeout)
            res.append(self.child.before)
            self.child.sendline(line)           

        # Command was fully submitted, now wait for the next prompt
        prompt = self._expect_prompt(timeout=timeout)
        while prompt == 1:
            # res.append("$")
            res.append(self.child.before)          
            # res.append("@")
            if not self.child.before: # real prompt at start of line
                self.child.sendline("") # empty line
            else: 
                # res.append("[")
                res.append(self.child.after)
                # res.append("]")              
            prompt = self._expect_prompt(timeout=timeout)
        
        while prompt == 0 and self.child.before and \
              (self.child.before[-1] == "n" or self.child.before[-1] == "-"):
            # res.append("#")
            res.append(self.child.before)
            # res.append(">> ") # ???
            # self.child.sendline("")    (deze moet echt niet...)        
            # res.append("(")
            res.append(self.child.after)
            # res.append(")")           
            prompt = self._expect_prompt(timeout=timeout)
            
        if  prompt == 1:
            # We got the continuation prompt - command was incomplete
            self.child.kill(signal.SIGINT)
            self._expect_prompt(timeout=1)
            return u''.join(res + [self.child.before, "ERROR, incomplete input!"])
            # raise ValueError("Continuation prompt found - input was incomplete:\n"
            #                  + command)
            
        return u''.join(res + [self.child.before])


class ElmReplKernel(Kernel):
    implementation = 'ElmReplKernel'
    implementation_version = '0.1'
    language = 'no-op'
    language_version = '0.1'
    language_info = {
        'name': 'elm',
        'codemirror_mode': 'elm',
        'mimetype': 'text/x-elm',
        'file_extension': '.elm',
    }
    banner = "Elm REPL kernel"

    def __init__(self, **kwargs):
        Kernel.__init__(self, **kwargs)
        self._start_elm()

    def _start_elm(self):
        # init Elm Repl Wrapper
        self.elmrepl = ElmWrapper()

    def do_execute(self, code, silent, store_history=True, user_expressions=None,
                   allow_stdin=False):
        if not silent:
            result_string = self.elmrepl.run_command(code)
            stream_content = {'name': 'stdout', 'text': result_string}
            self.send_response(self.iopub_socket, 'stream', stream_content)

        return {'status': 'ok',
                # The base class increments the execution count
                'execution_count': self.execution_count,
                'payload': [],
                'user_expressions': {},
               }
