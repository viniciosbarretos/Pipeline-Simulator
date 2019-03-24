# Code by
# Vinicios Barretos
# Thiago Leal

# Pipeline stages constants
FETCH_INSTRUCTION = 0
DECODE_INSTRUCTION = 1
CALC_OPERANDS = 2
FETCH_OPERANDS = 3
EXECUTE_INSTRUCTION = 4
WRITE_OPERANDS = 5


class Register:
    def __init__(self, esp):
        self.registers = {'ebp': 0, 'eax': 0, 'temp': 0, 'temp2': 0, 'esp': esp, 'cmp': 0}

    # Get the value from a register.
    def get_value(self, register):
        return self.registers[register]

    # Put a number on register1 or copy the value from register2.
    def movl(self, register1, register2):
        if register2.isdigit():
            self.registers[register1] = register2
        else:
            self.registers[register1] = self.registers[register2]

    # Subtract
    def cmpl(self, register1, register2):
        if register2.isdigit():
            self.registers['cmp'] = register2 - int(self.registers[register1])
        else:
            self.registers['cmp'] = int(self.registers[register2]) - int(self.registers[register1])

    # Add to the value of register1 any number or the value of register2.
    def addl(self, register1, register2):
        if register2.isdigit():
            self.registers[register1] += int(register2)
        else:
            self.registers[register1] = int(self.registers[register1]) + int(self.registers[register2])

    # Increases the value of the register1
    def incl(self, register):
        self.registers[register] = int(self.registers[register]) + 1

    def print_register(self):
        print('\n+', '-' * 44, '+', sep='')
        print('|', end='')
        for x in self.registers:
            print('%7s' % x, end='')
        print('  |\n|', end='')
        for x in self.registers:
            print('%7s' % self.registers.get(x), end='')
        print('  |')
        print('+', '-' * 44, '+\n', sep='')


class Instructions:
    instructions = []
    id = 0

    def add_instruction(self, instruction):
        self.instructions.append(instruction)

    @staticmethod
    def new_instruction(instruction, args, id):

        # Return the instruction object.
        return {'instruction': instruction, 'args': args, 'id': id}

    def read_instruction(self, line):
        # Remove comments
        line = line.split('//')[0]
        # Clean the str.
        line = line.replace('\t', ' ')
        line = line.replace(',', ' ')
        # Get a list of commands.
        line = line.split()

        # Get the instruction object.
        instruction = self.new_instruction(line[0], line[1:], self.id)
        self.id += 1

        # Save instruction on list.
        self.add_instruction(instruction)

    def get_instruction(self, index):
        return self.instructions[index]

    def get_len(self):
        return len(self.instructions)


def execute(command, registers):
    if command['instruction'] == 'jmp':
        return command['args'][0]

    elif command['instruction'] == 'movl':
        registers.movl(command['args'][0], command['args'][1])
        return None

    elif command['instruction'] == 'addl':
        registers.addl(command['args'][0], command['args'][1])
        return None

    elif command['instruction'] == 'incl':
        registers.incl(command['args'][0])
        return None

    elif command['instruction'] == 'cmpl':
        registers.cmpl(command['args'][0], command['args'][1])
        return None

    elif command['instruction'] == 'jle':
        if registers.get_value('cmp') >= 0:
            return command['args'][0]

    elif command['instruction'] == 'ret':
        return 'Exit'

    return None


class Tags:
    tags = []

    def add_tag(self, tag, line):
        self.tags.append(self.new_tag(tag, line))

    def print_tags(self):
        print(self.tags)

    @staticmethod
    def new_tag(tag, line):
        # Clean the tag.
        tag = tag.replace(':', '')
        tag = tag.replace('\t', '')
        tag = tag.replace(' ', '')

        # Return the tag object.
        return {'tag': tag, 'line': line}

    def get_line(self, tag):
        # Search the line number by given a tag name.
        for t in self.tags:
            if t['tag'] == tag:
                return t['line']

        return None


class Command:
    def __init__(self, command):
        self.command = {'command': command, 'stage': 0}

    def get_stage(self):
        return self.command['stage']

    def get_command(self):
        return self.command['command']

    def next_stage(self):
        self.command['stage'] += 1

    def print(self):
        print(self.command)


class Pipeline:
    def __init__(self):
        self.pipeline = []
        self.matrix = [
            ['FI', 'DI', 'CO', 'FO', 'EI', 'WO',],
        ]

    def print_pipeline(self):
        for x in self.matrix:
            print(' ', end='')
            for y in x:
                print('%7s' % y, end='')
            print()

    def add_print(self, stage, command):
        self.matrix[-1][stage] = command

    def add_command(self, command):
        self.pipeline.append(Command(command))

    def exec_pipeline(self, registers):
        response = None
        remove = False

        # Add a new blank line to print matrix.
        self.matrix.append([])
        for x in range(0,6):
            self.matrix[-1].append('')

        # Iterate over pipeline commands and change it states
        for c in self.pipeline:

            # Just go to the next step.
            if c.get_stage() < EXECUTE_INSTRUCTION:
                # Print line stage.
                self.add_print(c.get_stage(), str(c.get_command()['id']))

                # Go to next stage.
                c.next_stage()

            # Execute the command
            elif c.get_stage() == EXECUTE_INSTRUCTION:
                # Update registers and get new line on a jump.
                response = execute(c.get_command(), registers)

                # Print line stage.
                self.add_print(c.get_stage(), str(c.get_command()['id']))

                # Go to next stage.
                c.next_stage()

            # Command end, remove them.
            else:
                # Print line stage.
                self.add_print(c.get_stage(), str(c.get_command()['id']))

                # Remove line from pipeline.
                remove = True

        if remove:
            self.pipeline.pop(0)

        # self.print_pipeline()

        return response

    def clean_pipeline(self):
        to_be_removed = []
        # Remove any command that not execute yet
        for c in self.pipeline:
            if c.get_stage() in range(FETCH_INSTRUCTION, WRITE_OPERANDS):
                to_be_removed.append(c)
        for x in range(0, len(to_be_removed)):
            self.pipeline.remove(to_be_removed[x])


class Interpreter:

    def __init__(self, code, esp):
        self.registers = Register(esp)
        self.code = code.split('\n')
        self.instructions = Instructions()
        self.pipeline = Pipeline()
        self.tags = Tags()
        self.line = 0
        self.max_line = 0

    def parse_code(self):

        # Parse all the lines and store in the vectors.
        for line in self.code:
            self.parse_line(line)

        # Store the last line.
        self.max_line = self.line
        # Reset the line counter.
        self.line = 0

    def parse_line(self, line):
        # Read the instruction from the string.
        if line[0] == '\t' or line[0] == ' ':
            self.instructions.read_instruction(line)
            self.line += 1
            pass

        # Read the tag from the string.
        else:
            self.tags.add_tag(line, self.line)

    def print_pipeline(self, response):
        # Print pipeline.
        self.pipeline.print_pipeline()

        # Print register header
        self.registers.print_register()

    def run_cycle(self):
        # Add new instruction to pipeline
        if self.line < self.max_line:
            self.pipeline.add_command(self.instructions.get_instruction(self.line))

        # Run a clock on pipeline.
        tag = self.pipeline.exec_pipeline(self.registers)

        # Print the current stage of the pipeline.
        self.print_pipeline(tag)

        # No jump, go to the next line.
        if tag is None:
            self.line += 1

        # Program ended.
        elif tag is 'Exit':
            return False

        # Jump for the tag
        else:
            # Clean the pipeline
            self.pipeline.clean_pipeline()

            # Go to the new line
            self.line = self.tags.get_line(tag)
            print('==> Go to line:', self.line)

        return True


def get_int_number(text):
    is_valid = False
    answer = ''

    while not is_valid:
        answer = input(text)
        try:
            answer = int(answer)
            is_valid = True
        except:
            print('Error: not integer input!\n')

    return answer


if __name__ == '__main__':
    # Get the file.
    filename = input('Enter with the file name: ')
    file = None
    try:
        file = open(filename, 'r+')
    except FileNotFoundError:
        print('The file can\'t be reached.')
        exit()

    # Get the initial value.
    esp = get_int_number("Enter a value to esp: ")

    # Compile the code.
    i = Interpreter(file.read(), esp)
    i.parse_code()

    # Run interactively.
    run = True
    while run:
        input('\nPress enter to next step...\n\n')
        run = i.run_cycle()
