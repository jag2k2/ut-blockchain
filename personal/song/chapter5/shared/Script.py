from logging import Logger
from shared.Utility import encode_varint, int_to_little_endian, little_endian_to_int, read_varint

class Script:
    
    def __init__(self, cmds=None):
        if cmds is None:
            self.cmds = []
        else:
            self.cmds = cmds

    def __add__(self, other):
        return Script(self.cmds + other.cmds)

    def raw_serialize(self):
        result = b''
        for cmd in self.cmds:
            if type(cmd) == int:    #if this is an integer, cmd is an opcode
                result += int_to_little_endian(cmd, 1)
            else:
                length = len(cmd)
                if length < 75:     #if length is between 1 and 75, encode the length as a single byte
                    result += int_to_little_endian(length, 1)
                elif length > 75 and length < 0x100:
                    result += int_to_little_endian(76, 1)
                    result += int_to_little_endian(length, 1)
                elif length >= 0x100 and length <= 520:
                    result += int_to_little_endian(77, 1)
                    result += int_to_little_endian(length, 2)
                else:
                    raise ValueError('too long a command')
                result += cmd
        return result

    def serialize(self):
        result = self.raw_serialize()
        total = len(result)
        return encode_varint(total) + result
                
    @classmethod
    def parse(cls, stream):
        script_length = read_varint(stream)
        cmds = []
        count = 0
        while count < script_length:
            current = stream.read(1)
            count += 1
            current_byte = current[0]
            if current_byte >= 1 and current_byte <= 75: # next n bytes are an element
                n = current_byte
                cmds.append(stream.read(n))
                count += n
            elif current_byte == 76:    # OP_PUSHDATA1 so the next byte tells us how many bytes to read
                data_length = little_endian_to_int(stream.read(1))
                cmds.append(stream.read(data_length))
                count += data_length + 1
            elif current_byte == 77:    # OP_PUSHDATA2 so the next 2 bytes tells us how many bytes to read
                data_length = little_endian_to_int(stream.read(2))
                cmds.append(stream.read(data_length))
                count += data_length + 2
            else:
                op_code = current_byte
                cmds.append(op_code)
        if count != script_length:
            raise SyntaxError('parsing script failed')
        return cls(cmds)